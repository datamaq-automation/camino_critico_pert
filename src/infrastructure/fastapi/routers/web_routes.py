import json
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Depends, Form, Request, status
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from src.adapters.pert.controllers.pert_controller import PertController
from src.application.pert.dtos.activity_dto import ActivityInputDTO, ProjectInputDTO
from src.domain.pert.exceptions import PertDomainError
from src.infrastructure.fastapi.dependencies import get_pert_controller

templates_dir = Path(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))

router = APIRouter(include_in_schema=False)


@router.get("/", response_class=HTMLResponse)
def index_view(request: Request) -> Any:
    """Renderiza la vista principal para ingreso y edición de actividades."""
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"error_message": None},
    )


@router.post("/calculate", response_class=HTMLResponse)
def calculate_web_view(
    request: Request,
    activities_json: str = Form(...),
    target_duration: float | None = Form(None),
    controller: PertController = Depends(get_pert_controller),
) -> Any:
    """Procesa el formulario web y renderiza la vista de resultados interactiva."""
    try:
        raw_activities = json.loads(activities_json)
        activities: list[ActivityInputDTO] = [ActivityInputDTO(**item) for item in raw_activities]

        project_input = ProjectInputDTO(
            activities=activities,
            target_duration=target_duration if (target_duration is not None and target_duration > 0) else None,
        )

        calc_result = controller.process_project(project_input)

        return templates.TemplateResponse(
            request=request,
            name="result.html",
            context={
                "result": calc_result["result"],
                "vis_graph": calc_result["vis_graph"],
                "mermaid_code": calc_result["mermaid_code"],
            },
        )
    except PertDomainError as exc:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={"error_message": f"Error en el grafo: {exc}"},
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )
    except Exception as exc:
        return templates.TemplateResponse(
            request=request,
            name="index.html",
            context={"error_message": f"Error en los datos ingresados: {exc}"},
            status_code=status.HTTP_400_BAD_REQUEST,
        )
