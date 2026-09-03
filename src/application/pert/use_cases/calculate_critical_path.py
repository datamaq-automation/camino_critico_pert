from src.application.pert.dtos.activity_dto import CriticalPathResponseDTO, ProjectInputDTO
from src.application.pert.mappers.pert_mapper import PertMapper
from src.domain.pert.entities import Activity, ProbabilityResult
from src.domain.pert.services import CpmPertCalculator, PertProbabilityCalculator


class CalculateCriticalPathUseCase:
    """Caso de uso para orquestar el cálculo del Camino Crítico y análisis PERT."""

    def execute(self, project_input: ProjectInputDTO) -> CriticalPathResponseDTO:
        """Ejecuta el flujo completo de cálculo de CPM y PERT."""
        # Mapeo de DTOs de entrada a entidades de dominio
        activities: list[Activity] = [PertMapper.dto_to_activity(dto) for dto in project_input.activities]

        # Invocación del servicio de dominio
        calculation_result = CpmPertCalculator.calculate(activities)

        # Cálculo de probabilidad opcional si se suministró target_duration
        probability_result: ProbabilityResult | None = None
        if project_input.target_duration is not None:
            probability_result = PertProbabilityCalculator.calculate_probability(
                target_duration=project_input.target_duration,
                expected_duration=calculation_result.project_duration,
                critical_std_dev=calculation_result.critical_std_dev,
            )

        # Retorno de DTO formateado
        return PertMapper.domain_to_response_dto(
            result=calculation_result,
            probability_result=probability_result,
        )
