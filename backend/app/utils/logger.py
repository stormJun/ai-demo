import logging
import os
from logging.handlers import RotatingFileHandler

from app.config import settings


def setup_logger() -> logging.Logger:
    """Configure application logger; idempotent to avoid duplicate handlers."""
    logger = logging.getLogger("translator")
    logger.setLevel(settings.LOG_LEVEL)

    if logger.handlers:
        return logger

    log_dir = os.path.dirname(settings.LOG_FILE) or "."
    os.makedirs(log_dir, exist_ok=True)

    file_handler = RotatingFileHandler(
        settings.LOG_FILE,
        maxBytes=10 * 1024 * 1024,
        backupCount=5,
    )
    file_handler.setFormatter(logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s"))
    logger.addHandler(file_handler)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    logger.addHandler(console_handler)

    return logger


logger = setup_logger()

