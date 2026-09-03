from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from src.infrastructure.fastapi.routers import api_v1, web_routes
from src.infrastructure.settings.config import get_settings
from src.infrastructure.settings.logger import logger


def create_app() -> FastAPI:
    """Fábrica de inicialización de la aplicación FastAPI."""
    settings = get_settings()

    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        debug=settings.DEBUG,
    )

    # Configuración de CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.ALLOWED_HOSTS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Montaje de archivos estáticos
    static_dir = Path(__file__).resolve().parent / "infrastructure" / "fastapi" / "static"
    if static_dir.exists():
        app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

    # Inclusión de Routers
    app.include_router(web_routes.router)
    app.include_router(api_v1.router)

    logger.info(f"Aplicación '{settings.PROJECT_NAME}' v{settings.VERSION} iniciada exitosamente.")
    return app


app = create_app()
