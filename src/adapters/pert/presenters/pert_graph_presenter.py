from typing import Any
from src.application.pert.dtos.activity_dto import CriticalPathResponseDTO


class PertGraphPresenter:
    """Presentador encargado de convertir los resultados de CPM/PERT en estructuras para Vis.js y Mermaid.js."""

    @staticmethod
    def to_vis_network(response: CriticalPathResponseDTO) -> dict[str, list[dict[str, Any]]]:
        """Genera la estructura de nodos y aristas para la librería vis-network."""
        nodes: list[dict[str, Any]] = []
        edges: list[dict[str, Any]] = []

        act_map = {act.id: act for act in response.activities}

        # Construcción de Nodos
        for act in response.activities:
            tw = act.time_window
            is_crit = act.is_critical

            # Etiqueta estructurada estilo tarjeta PERT (AON)
            label = (
                f"[{act.id}] {act.name}\n"
                f"Dur: {act.duration} | Holgura: {tw.total_slack}\n"
                f"ES: {tw.early_start} | EF: {tw.early_finish}\n"
                f"LS: {tw.late_start} | LF: {tw.late_finish}"
            )

            # Estilos visuales
            if is_crit:
                bg_color = "#fee2e2"
                border_color = "#dc2626"
                border_width = 3
                font_color = "#7f1d1d"
            else:
                bg_color = "#f0fdf4"
                border_color = "#16a34a"
                border_width = 1.5
                font_color = "#14532d"

            nodes.append({
                "id": act.id,
                "label": label,
                "shape": "box",
                "margin": 12,
                "color": {
                    "background": bg_color,
                    "border": border_color,
                    "highlight": {
                        "background": bg_color,
                        "border": "#b91c1c" if is_crit else "#15803d",
                    },
                },
                "borderWidth": border_width,
                "font": {
                    "color": font_color,
                    "face": "monospace",
                    "size": 13,
                    "align": "center",
                },
                "is_critical": is_crit,
                "duration": act.duration,
                "early_start": tw.early_start,
                "early_finish": tw.early_finish,
                "late_start": tw.late_start,
                "late_finish": tw.late_finish,
                "total_slack": tw.total_slack,
            })

            # Construcción de Aristas
            for pred_id in act.predecessors:
                if pred_id not in act_map:
                    continue
                pred_act = act_map[pred_id]

                # Determinar si la conexión pertenece al camino crítico:
                # Ambas actividades son críticas y hay continuidad temporal (EF_pred == ES_act)
                is_crit_edge = (
                    is_crit
                    and pred_act.is_critical
                    and abs(pred_act.time_window.early_finish - tw.early_start) < 1e-6
                )

                edges.append({
                    "from": pred_id,
                    "to": act.id,
                    "arrows": "to",
                    "color": {
                        "color": "#dc2626" if is_crit_edge else "#94a3b8",
                        "highlight": "#b91c1c" if is_crit_edge else "#64748b",
                    },
                    "width": 3 if is_crit_edge else 1.5,
                    "dashes": False,
                    "smooth": {"type": "cubicBezier", "roundness": 0.2},
                })

        return {"nodes": nodes, "edges": edges}

    @staticmethod
    def to_mermaid(response: CriticalPathResponseDTO) -> str:
        """Genera el código sintáctico para renderizar con Mermaid.js."""
        lines: list[str] = ["graph LR"]

        # Definir nodos y conexiones
        for act in response.activities:
            safe_name = act.name.replace('"', "'")
            lines.append(f'    {act.id}["{act.id}: {safe_name} (Dur: {act.duration})"]')

        for act in response.activities:
            for pred_id in act.predecessors:
                lines.append(f"    {pred_id} --> {act.id}")

        # Aplicar estilos a actividades críticas
        critical_ids = [act.id for act in response.activities if act.is_critical]
        if critical_ids:
            for crit_id in critical_ids:
                lines.append(f"    style {crit_id} fill:#fee2e2,stroke:#dc2626,stroke-width:3px,color:#991b1b")

        return "\n".join(lines)
