from dataclasses import dataclass

from src.domain.pert.exceptions import InvalidDurationError


@dataclass(frozen=True)
class DurationEstimate:
    """Representa la estimación de tiempo de una actividad.

    Permite estimaciones determinísticas (CPM: optimista = probable = pesimista)
    o probabilísticas (PERT: optimista <= más probable <= pesimista).
    """

    optimistic: float
    most_likely: float
    pessimistic: float

    def __post_init__(self) -> None:
        if self.optimistic < 0 or self.most_likely < 0 or self.pessimistic < 0:
            raise InvalidDurationError("Las duraciones no pueden ser negativas.")
        if not (self.optimistic <= self.most_likely <= self.pessimistic):
            raise InvalidDurationError(
                f"Las duraciones deben cumplir Optimista ({self.optimistic}) <= "
                f"Más Probable ({self.most_likely}) <= Pesimista ({self.pessimistic})."
            )

    @property
    def expected_duration(self) -> float:
        """Calcula la duración esperada TE = (o + 4m + p) / 6."""
        return (self.optimistic + (4.0 * self.most_likely) + self.pessimistic) / 6.0

    @property
    def variance(self) -> float:
        """Calcula la varianza PERT: sigma^2 = ((p - o) / 6)^2."""
        return ((self.pessimistic - self.optimistic) / 6.0) ** 2.0

    @property
    def standard_deviation(self) -> float:
        """Desviación estándar de la actividad."""
        return (self.pessimistic - self.optimistic) / 6.0


@dataclass(frozen=True)
class TimeWindow:
    """Ventana de tiempos y holguras calculadas para una actividad en el método del camino crítico."""

    early_start: float
    early_finish: float
    late_start: float
    late_finish: float
    total_slack: float
    free_slack: float
    is_critical: bool
