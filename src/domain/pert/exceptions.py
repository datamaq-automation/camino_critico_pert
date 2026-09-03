class PertDomainError(Exception):
    """Excepción base para errores de dominio en PERT / CPM."""


class CycleDetectedError(PertDomainError):
    """Lanzada cuando el grafo de actividades contiene uno o más ciclos (bucles cerrados)."""


class ActivityNotFoundError(PertDomainError):
    """Lanzada cuando una actividad referenciada como predecesora no existe."""


class DuplicateActivityError(PertDomainError):
    """Lanzada cuando se intenta agregar una actividad con un identificador ya existente."""


class InvalidDurationError(PertDomainError):
    """Lanzada cuando las duraciones estimadas son inválidas (negativas o no cumplen optimista <= más_probable <= pesimista)."""


class EmptyProjectError(PertDomainError):
    """Lanzada cuando el proyecto no contiene actividades a calcular."""
