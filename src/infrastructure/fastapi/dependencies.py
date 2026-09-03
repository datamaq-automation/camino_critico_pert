from src.adapters.pert.controllers.pert_controller import PertController
from src.application.pert.use_cases.calculate_critical_path import CalculateCriticalPathUseCase
from src.infrastructure.settings.config import Settings, get_settings


def get_calculate_use_case() -> CalculateCriticalPathUseCase:
    """Proveedor de inyección de dependencias para CalculateCriticalPathUseCase."""
    return CalculateCriticalPathUseCase()


def get_pert_controller() -> PertController:
    """Proveedor de inyección de dependencias para PertController."""
    use_case = get_calculate_use_case()
    return PertController(use_case=use_case)


def get_app_settings() -> Settings:
    """Proveedor de configuración de la aplicación."""
    return get_settings()
