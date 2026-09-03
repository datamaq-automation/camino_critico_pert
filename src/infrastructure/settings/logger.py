import logging
import sys

from src.infrastructure.settings.config import get_settings


def setup_logging() -> logging.Logger:
    """Configura el logging centralizado estructurado."""
    settings = get_settings()
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)],
    )
    logger = logging.getLogger(settings.PROJECT_NAME)
    logger.setLevel(log_level)
    return logger


logger = setup_logging()
