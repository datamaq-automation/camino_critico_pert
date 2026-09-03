import pytest

from src.domain.pert.entities import Activity
from src.domain.pert.exceptions import (
    ActivityNotFoundError,
    CycleDetectedError,
    DuplicateActivityError,
    EmptyProjectError,
    InvalidDurationError,
)
from src.domain.pert.services import CpmPertCalculator, PertProbabilityCalculator
from src.domain.pert.value_objects import DurationEstimate


def test_deterministic_cpm_classic_example() -> None:
    # Ejemplo clásico de libro de Investigación Operativa / Gestión de Proyectos:
    # A (3, pred: []), B (4, pred: []), C (2, pred: [A]), D (5, pred: [B]), E (3, pred: [C, D])
    # Caminos:
    # A -> C -> E: 3 + 2 + 3 = 8
    # B -> D -> E: 4 + 5 + 3 = 12 (Camino Crítico: B -> D -> E, duración = 12)
    activities = [
        Activity(id="A", name="Diseño A", estimate=DurationEstimate(3, 3, 3), predecessors=[]),
        Activity(id="B", name="Diseño B", estimate=DurationEstimate(4, 4, 4), predecessors=[]),
        Activity(id="C", name="Desarrollo A", estimate=DurationEstimate(2, 2, 2), predecessors=["A"]),
        Activity(id="D", name="Desarrollo B", estimate=DurationEstimate(5, 5, 5), predecessors=["B"]),
        Activity(id="E", name="Integración", estimate=DurationEstimate(3, 3, 3), predecessors=["C", "D"]),
    ]

    result = CpmPertCalculator.calculate(activities)

    assert result.project_duration == 12.0
    assert result.critical_paths == [["B", "D", "E"]]

    # Verificar tiempos y holguras
    act_map = {a.id: a for a in result.activities}

    # B es crítica: ES=0, EF=4, LS=0, LF=4, Slack=0
    assert act_map["B"].time_window.early_start == 0.0
    assert act_map["B"].time_window.early_finish == 4.0
    assert act_map["B"].time_window.late_start == 0.0
    assert act_map["B"].time_window.late_finish == 4.0
    assert act_map["B"].time_window.total_slack == 0.0
    assert act_map["B"].is_critical is True

    # D es crítica: ES=4, EF=9, LS=4, LF=9, Slack=0
    assert act_map["D"].time_window.early_start == 4.0
    assert act_map["D"].time_window.early_finish == 9.0
    assert act_map["D"].time_window.late_start == 4.0
    assert act_map["D"].time_window.late_finish == 9.0
    assert act_map["D"].time_window.total_slack == 0.0
    assert act_map["D"].is_critical is True

    # E es crítica: ES=9, EF=12, LS=9, LF=12, Slack=0
    assert act_map["E"].time_window.early_start == 9.0
    assert act_map["E"].time_window.early_finish == 12.0
    assert act_map["E"].time_window.total_slack == 0.0
    assert act_map["E"].is_critical is True

    # A no es crítica: Dur=3, EF=3, C empieza a max(EF(A))=3. E requiere C y D.
    # D termina en 9, por lo que C puede terminar hasta 9 (LF(C)=9).
    # Como C dura 2, LS(C)=7. Entonces LF(A)=7.
    # Con Dur(A)=3, LS(A)=4, ES(A)=0, Slack(A)=4.
    assert act_map["A"].time_window.early_start == 0.0
    assert act_map["A"].time_window.early_finish == 3.0
    assert act_map["A"].time_window.late_finish == 7.0
    assert act_map["A"].time_window.late_start == 4.0
    assert act_map["A"].time_window.total_slack == 4.0
    assert act_map["A"].is_critical is False


def test_pert_probabilistic_calculations() -> None:
    # Actividad con 3 estimaciones: o=2, m=5, p=8
    # TE = (2 + 4*5 + 8) / 6 = 30 / 6 = 5.0
    # Varianza = ((8 - 2) / 6)^2 = (6 / 6)^2 = 1.0
    est = DurationEstimate(optimistic=2.0, most_likely=5.0, pessimistic=8.0)
    assert est.expected_duration == 5.0
    assert est.variance == 1.0
    assert est.standard_deviation == 1.0

    activities = [
        Activity(id="X", name="Tarea X", estimate=est, predecessors=[]),
        Activity(id="Y", name="Tarea Y", estimate=DurationEstimate(3.0, 6.0, 9.0), predecessors=["X"]),
    ]
    # Y: TE = (3 + 24 + 9)/6 = 36/6 = 6.0. Varianza = ((9-3)/6)^2 = 1.0
    result = CpmPertCalculator.calculate(activities)

    assert result.project_duration == 11.0  # 5 + 6
    assert result.critical_variance == 2.0  # 1.0 + 1.0
    assert round(result.critical_std_dev, 4) == round(2.0**0.5, 4)

    # Probabilidad de terminar en 11 (plazo = esperado -> Z=0 -> Prob=50%)
    prob_result = PertProbabilityCalculator.calculate_probability(
        target_duration=11.0,
        expected_duration=result.project_duration,
        critical_std_dev=result.critical_std_dev,
    )
    assert prob_result.z_score == 0.0
    assert prob_result.probability == 0.5


def test_cycle_detection_raises_error() -> None:
    activities = [
        Activity(id="A", name="A", estimate=DurationEstimate(1, 1, 1), predecessors=["B"]),
        Activity(id="B", name="B", estimate=DurationEstimate(1, 1, 1), predecessors=["A"]),
    ]
    with pytest.raises(CycleDetectedError):
        CpmPertCalculator.calculate(activities)


def test_self_predecessor_raises_cycle_error() -> None:
    activities = [
        Activity(id="A", name="A", estimate=DurationEstimate(1, 1, 1), predecessors=["A"]),
    ]
    with pytest.raises(CycleDetectedError):
        CpmPertCalculator.calculate(activities)


def test_missing_predecessor_raises_error() -> None:
    activities = [
        Activity(id="A", name="A", estimate=DurationEstimate(1, 1, 1), predecessors=["INEXISTENTE"]),
    ]
    with pytest.raises(ActivityNotFoundError):
        CpmPertCalculator.calculate(activities)


def test_duplicate_activity_raises_error() -> None:
    activities = [
        Activity(id="A", name="A1", estimate=DurationEstimate(1, 1, 1), predecessors=[]),
        Activity(id="A", name="A2", estimate=DurationEstimate(2, 2, 2), predecessors=[]),
    ]
    with pytest.raises(DuplicateActivityError):
        CpmPertCalculator.calculate(activities)


def test_empty_project_raises_error() -> None:
    with pytest.raises(EmptyProjectError):
        CpmPertCalculator.calculate([])


def test_invalid_duration_estimate_raises_error() -> None:
    with pytest.raises(InvalidDurationError):
        # optimista mayor que probable
        DurationEstimate(optimistic=10.0, most_likely=5.0, pessimistic=15.0)

    with pytest.raises(InvalidDurationError):
        # duración negativa
        DurationEstimate(optimistic=-1.0, most_likely=2.0, pessimistic=3.0)
