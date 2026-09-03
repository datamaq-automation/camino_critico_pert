from dataclasses import dataclass, field

from src.domain.pert.value_objects import DurationEstimate, TimeWindow


@dataclass
class Activity:
    """Entidad que representa una actividad del proyecto."""

    id: str
    name: str
    estimate: DurationEstimate
    predecessors: list[str] = field(default_factory=lambda: list[str]())
    time_window: TimeWindow | None = None

    @property
    def duration(self) -> float:
        return self.estimate.expected_duration

    @property
    def variance(self) -> float:
        return self.estimate.variance

    @property
    def is_critical(self) -> bool:
        return self.time_window.is_critical if self.time_window is not None else False


@dataclass(frozen=True)
class CriticalPathResult:
    """Resultado completo del análisis de Camino Crítico (CPM / PERT)."""

    activities: list[Activity]
    critical_paths: list[list[str]]
    project_duration: float
    critical_variance: float
    critical_std_dev: float


@dataclass(frozen=True)
class ProbabilityResult:
    """Resultado del cálculo probabilístico PERT para un plazo meta dado."""

    target_duration: float
    expected_duration: float
    z_score: float
    probability: float
