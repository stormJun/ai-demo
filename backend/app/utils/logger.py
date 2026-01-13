import logging

from app.config import settings


def setup_logger() -> logging.Logger:
    """Configure application logger; idempotent to avoid duplicate handlers."""
    logger = logging.getLogger("translator")
    logger.setLevel(settings.LOG_LEVEL)

    if logger.handlers:
        return logger

    # Only console output for serverless environments (Vercel, AWS Lambda, etc.)
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
    logger.addHandler(console_handler)

    return logger


logger = setup_logger()

