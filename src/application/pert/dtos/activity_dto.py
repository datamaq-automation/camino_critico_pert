from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class ActivityInputDTO(BaseModel):
    """DTO para la entrada de datos de una actividad."""
    model_config = ConfigDict(extra="forbid")

    id: str = Field(..., min_length=1, max_length=50, description="Identificador único de la actividad (ej. A, T1)")
    name: str = Field(..., min_length=1, max_length=200, description="Nombre descriptivo de la actividad")
    optimistic: float = Field(..., ge=0.0, description="Duración optimista (o)")
    most_likely: float = Field(..., ge=0.0, description="Duración más probable (m)")
    pessimistic: float = Field(..., ge=0.0, description="Duración pesimista (p)")
    predecessors: list[str] = Field(default_factory=list, description="Lista de IDs de actividades predecesoras")


class ProjectInputDTO(BaseModel):
    """DTO para procesar un proyecto completo."""
    model_config = ConfigDict(extra="forbid")

    activities: list[ActivityInputDTO] = Field(..., min_length=1, description="Lista de actividades del proyecto")
    target_duration: Optional[float] = Field(None, ge=0.0, description="Plazo meta opcional para cálculo de probabilidad PERT")


class TimeWindowDTO(BaseModel):
    """DTO que encapsula tiempos y holguras calculadas."""
    model_config = ConfigDict(from_attributes=True)

    early_start: float
    early_finish: float
    late_start: float
    late_finish: float
    total_slack: float
    free_slack: float
    is_critical: bool


class ActivityResultDTO(BaseModel):
    """DTO con el resultado calculado para una actividad."""
    model_config = ConfigDict(from_attributes=True)

    id: str
    name: str
    duration: float
    variance: float
    predecessors: list[str]
    time_window: TimeWindowDTO
    is_critical: bool


class ProbabilityDTO(BaseModel):
    """DTO para la probabilidad estadística calculada."""
    model_config = ConfigDict(from_attributes=True)

    target_duration: float
    expected_duration: float
    z_score: float
    probability: float
    probability_percentage: float


class CriticalPathResponseDTO(BaseModel):
    """DTO con la respuesta integral del cálculo de camino crítico y PERT."""
    model_config = ConfigDict(from_attributes=True)

    activities: list[ActivityResultDTO]
    critical_paths: list[list[str]]
    project_duration: float
    critical_variance: float
    critical_std_dev: float
    probability: Optional[ProbabilityDTO] = None
