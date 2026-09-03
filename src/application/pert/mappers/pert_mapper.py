from src.application.pert.dtos.activity_dto import (
    ActivityInputDTO,
    ActivityResultDTO,
    CriticalPathResponseDTO,
    ProbabilityDTO,
    TimeWindowDTO,
)
from src.domain.pert.entities import Activity, CriticalPathResult, ProbabilityResult
from src.domain.pert.value_objects import DurationEstimate


class PertMapper:
    """Mapeador canónico bidireccional entre DTOs y Entidades de Dominio."""

    @staticmethod
    def dto_to_activity(dto: ActivityInputDTO) -> Activity:
        """Convierte un ActivityInputDTO en una entidad de dominio Activity."""
        estimate = DurationEstimate(
            optimistic=dto.optimistic,
            most_likely=dto.most_likely,
            pessimistic=dto.pessimistic,
        )
        return Activity(
            id=dto.id.strip(),
            name=dto.name.strip(),
            estimate=estimate,
            predecessors=[p.strip() for p in dto.predecessors if p.strip()],
        )

    @staticmethod
    def domain_to_response_dto(
        result: CriticalPathResult,
        probability_result: ProbabilityResult | None = None,
    ) -> CriticalPathResponseDTO:
        """Convierte los resultados del dominio a CriticalPathResponseDTO."""
        activity_dtos: list[ActivityResultDTO] = []

        for act in result.activities:
            if act.time_window is None:
                continue

            tw_dto = TimeWindowDTO(
                early_start=act.time_window.early_start,
                early_finish=act.time_window.early_finish,
                late_start=act.time_window.late_start,
                late_finish=act.time_window.late_finish,
                total_slack=act.time_window.total_slack,
                free_slack=act.time_window.free_slack,
                is_critical=act.time_window.is_critical,
            )

            activity_dtos.append(
                ActivityResultDTO(
                    id=act.id,
                    name=act.name,
                    duration=round(act.duration, 4),
                    variance=round(act.variance, 6),
                    predecessors=act.predecessors,
                    time_window=tw_dto,
                    is_critical=act.is_critical,
                )
            )

        prob_dto: ProbabilityDTO | None = None
        if probability_result is not None:
            prob_dto = ProbabilityDTO(
                target_duration=probability_result.target_duration,
                expected_duration=probability_result.expected_duration,
                z_score=probability_result.z_score,
                probability=probability_result.probability,
                probability_percentage=round(probability_result.probability * 100.0, 2),
            )

        return CriticalPathResponseDTO(
            activities=activity_dtos,
            critical_paths=result.critical_paths,
            project_duration=result.project_duration,
            critical_variance=result.critical_variance,
            critical_std_dev=result.critical_std_dev,
            probability=prob_dto,
        )
