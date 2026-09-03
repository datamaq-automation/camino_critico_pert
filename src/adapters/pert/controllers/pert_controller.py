from typing import Any
from src.adapters.pert.presenters.pert_graph_presenter import PertGraphPresenter
from src.application.pert.dtos.activity_dto import CriticalPathResponseDTO, ProjectInputDTO
from src.application.pert.use_cases.calculate_critical_path import CalculateCriticalPathUseCase


class PertController:
    """Controlador que procesa solicitudes de cálculo de Camino Crítico."""

    def __init__(self, use_case: CalculateCriticalPathUseCase) -> None:
        self._use_case = use_case

    def process_project(self, project_input: ProjectInputDTO) -> dict[str, Any]:
        """Ejecuta el cálculo y genera las estructuras de visualización."""
        response_dto: CriticalPathResponseDTO = self._use_case.execute(project_input)
        vis_graph = PertGraphPresenter.to_vis_network(response_dto)
        mermaid_code = PertGraphPresenter.to_mermaid(response_dto)

        return {
            "result": response_dto,
            "vis_graph": vis_graph,
            "mermaid_code": mermaid_code,
        }
