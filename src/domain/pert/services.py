import math

from src.domain.pert.entities import Activity, CriticalPathResult, ProbabilityResult
from src.domain.pert.exceptions import (
    ActivityNotFoundError,
    CycleDetectedError,
    DuplicateActivityError,
    EmptyProjectError,
)
from src.domain.pert.value_objects import TimeWindow


class CpmPertCalculator:
    """Servicio de dominio puro para el cálculo de Camino Crítico (CPM) y PERT."""

    @classmethod
    def calculate(cls, activities: list[Activity]) -> CriticalPathResult:
        """Ejecuta el Forward Pass, Backward Pass, cálculo de holguras y determinación de caminos críticos."""
        if not activities:
            raise EmptyProjectError("No hay actividades registradas en el proyecto.")

        activity_map: dict[str, Activity] = {}
        for act in activities:
            if act.id in activity_map:
                raise DuplicateActivityError(f"Actividad duplicada con ID '{act.id}'.")
            activity_map[act.id] = act

        # Validar predecesores
        for act in activities:
            for pred_id in act.predecessors:
                if pred_id == act.id:
                    raise CycleDetectedError(f"La actividad '{act.id}' no puede ser predecesora de sí misma.")
                if pred_id not in activity_map:
                    raise ActivityNotFoundError(f"Predecesora '{pred_id}' no encontrada para la actividad '{act.id}'.")

        # Construir listas de adyacencia
        successors: dict[str, list[str]] = {act.id: list[str]() for act in activities}
        in_degrees: dict[str, int] = {act.id: 0 for act in activities}

        for act in activities:
            for pred_id in act.predecessors:
                successors[pred_id].append(act.id)
                in_degrees[act.id] += 1

        # Ordenamiento topológico con Kahn (detección de ciclos)
        queue: list[str] = [act_id for act_id, deg in in_degrees.items() if deg == 0]
        topo_order: list[str] = list[str]()

        while len(queue) > 0:
            current_id = queue.pop(0)
            topo_order.append(current_id)

            for succ_id in successors[current_id]:
                in_degrees[succ_id] -= 1
                if in_degrees[succ_id] == 0:
                    queue.append(succ_id)

        if len(topo_order) != len(activities):
            raise CycleDetectedError("Se detectó un ciclo en el grafo de dependencias de actividades.")

        # 1. Forward Pass
        es: dict[str, float] = {}
        ef: dict[str, float] = {}

        for act_id in topo_order:
            act = activity_map[act_id]
            if len(act.predecessors) == 0:
                es[act_id] = 0.0
            else:
                es[act_id] = max(ef[p] for p in act.predecessors)
            ef[act_id] = es[act_id] + act.duration

        project_duration = max(ef.values()) if len(ef) > 0 else 0.0

        # 2. Backward Pass
        lf: dict[str, float] = {}
        ls: dict[str, float] = {}

        for act_id in reversed(topo_order):
            act = activity_map[act_id]
            succ_ids = successors[act_id]
            if len(succ_ids) == 0:
                lf[act_id] = project_duration
            else:
                lf[act_id] = min(ls[s] for s in succ_ids)
            ls[act_id] = lf[act_id] - act.duration

        # 3. Cálculo de Holguras y Asignación de TimeWindow
        for act in activities:
            act_id = act.id
            early_start = es[act_id]
            early_finish = ef[act_id]
            late_start = ls[act_id]
            late_finish = lf[act_id]

            total_slack = round(late_finish - early_finish, 6)
            # Evitar -0.0
            if abs(total_slack) < 1e-6:
                total_slack = 0.0

            succ_ids = successors[act_id]
            if len(succ_ids) == 0:
                free_slack = round(project_duration - early_finish, 6)
            else:
                free_slack = round(min(es[s] for s in succ_ids) - early_finish, 6)

            if abs(free_slack) < 1e-6:
                free_slack = 0.0

            is_critical = abs(total_slack) < 1e-6

            act.time_window = TimeWindow(
                early_start=round(early_start, 4),
                early_finish=round(early_finish, 4),
                late_start=round(late_start, 4),
                late_finish=round(late_finish, 4),
                total_slack=total_slack,
                free_slack=free_slack,
                is_critical=is_critical,
            )

        # 4. Determinación de Caminos Críticos
        critical_paths = cls._find_critical_paths(
            activities=activities,
            successors=successors,
            project_duration=project_duration,
        )

        # 5. Cálculo de varianza del camino crítico (usar el camino crítico con mayor varianza si hay múltiples)
        critical_variance = 0.0
        if len(critical_paths) > 0:
            variances: list[float] = []
            for path in critical_paths:
                path_var = sum(activity_map[node_id].variance for node_id in path)
                variances.append(path_var)
            critical_variance = max(variances)

        critical_std_dev = math.sqrt(critical_variance)

        return CriticalPathResult(
            activities=activities,
            critical_paths=critical_paths,
            project_duration=round(project_duration, 4),
            critical_variance=round(critical_variance, 6),
            critical_std_dev=round(critical_std_dev, 6),
        )

    @classmethod
    def _find_critical_paths(
        cls,
        activities: list[Activity],
        successors: dict[str, list[str]],
        project_duration: float,
    ) -> list[list[str]]:
        """Busca todas las secuencias completas de actividades críticas desde el inicio hasta el fin."""
        activity_map: dict[str, Activity] = {act.id: act for act in activities}
        critical_nodes: set[str] = {act.id for act in activities if act.is_critical}

        if not critical_nodes:
            return list[list[str]]()

        # Nodos iniciales críticos (ES == 0 o sin predecesores críticos)
        start_nodes: list[str] = [
            act.id
            for act in activities
            if act.is_critical and (act.time_window is not None and abs(act.time_window.early_start) < 1e-6)
        ]

        # Nodos finales críticos (EF == project_duration)
        end_nodes: set[str] = {
            act.id
            for act in activities
            if act.is_critical
            and (act.time_window is not None and abs(act.time_window.early_finish - project_duration) < 1e-6)
        }

        all_paths: list[list[str]] = list[list[str]]()

        def dfs(current_id: str, current_path: list[str]) -> None:
            if current_id in end_nodes:
                all_paths.append(list[str](current_path))
                return

            current_act = activity_map[current_id]
            current_ef = current_act.time_window.early_finish if current_act.time_window else 0.0

            for next_id in successors[current_id]:
                if next_id in critical_nodes:
                    next_act = activity_map[next_id]
                    next_es = next_act.time_window.early_start if next_act.time_window else 0.0
                    # Continuidad en el camino crítico: EF(u) == ES(v)
                    if abs(current_ef - next_es) < 1e-6:
                        current_path.append(next_id)
                        dfs(next_id, current_path)
                        current_path.pop()

        for start_id in start_nodes:
            dfs(start_id, [start_id])

        return all_paths


class PertProbabilityCalculator:
    """Calculador estadístico de probabilidades de culminación para proyectos PERT."""

    @staticmethod
    def calculate_probability(
        target_duration: float,
        expected_duration: float,
        critical_std_dev: float,
    ) -> ProbabilityResult:
        """Calcula el Z-score y la probabilidad acumulada P(T <= target_duration)."""
        if critical_std_dev <= 1e-9:
            # Varianza cero: determinístico
            if target_duration >= expected_duration:
                return ProbabilityResult(
                    target_duration=target_duration,
                    expected_duration=expected_duration,
                    z_score=0.0,
                    probability=1.0,
                )
            return ProbabilityResult(
                target_duration=target_duration,
                expected_duration=expected_duration,
                z_score=float("-inf"),
                probability=0.0,
            )

        z = (target_duration - expected_duration) / critical_std_dev
        # Función de distribución normal acumulada vía función de error (erf)
        prob = 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))
        prob = max(0.0, min(1.0, prob))

        return ProbabilityResult(
            target_duration=round(target_duration, 4),
            expected_duration=round(expected_duration, 4),
            z_score=round(z, 4),
            probability=round(prob, 4),
        )
