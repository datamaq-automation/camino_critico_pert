from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from src.adapters.pert.controllers.pert_controller import PertController
from src.application.pert.dtos.activity_dto import ActivityInputDTO, ProjectInputDTO
from src.domain.pert.exceptions import PertDomainError
from src.infrastructure.fastapi.dependencies import get_pert_controller
from src.infrastructure.graph.networkx_adapter import NetworkXAdapter

router = APIRouter(prefix="/api/v1/pert", tags=["PERT / CPM"])


@router.post("/calculate", status_code=status.HTTP_200_OK)
def calculate_critical_path(
    project_input: ProjectInputDTO,
    controller: PertController = Depends(get_pert_controller),
) -> dict[str, Any]:
    """Calcula el camino crítico, holguras y genera el grafo para vis-network y mermaid."""
    try:
        result = controller.process_project(project_input)
        return result
    except PertDomainError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno al calcular el proyecto: {exc}",
        ) from exc


@router.post("/validate-dag", status_code=status.HTTP_200_OK)
def validate_dag(activities: list[ActivityInputDTO]) -> dict[str, Any]:
    """Valida si el conjunto de actividades forma un Grafo Dirigido Acíclico (DAG) utilizando NetworkX."""
    graph = NetworkXAdapter.build_digraph(activities)
    is_dag, cycles = NetworkXAdapter.validate_acyclic(graph)
    metrics = NetworkXAdapter.analyze_graph_metrics(graph)

    return {
        "is_dag": is_dag,
        "cycles": cycles,
        "metrics": metrics,
        "topological_order": NetworkXAdapter.get_topological_order(graph) if is_dag else [],
    }
