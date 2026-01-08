from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application configuration."""

    # AI configuration
    QWEN_API_KEY: str = ""
    QWEN_MODEL: str = "qwen-turbo"

    # Service configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8100
    DEBUG: bool = False

    # Business configuration
    MAX_INPUT_LENGTH: int = 5000
    MIN_RECOGNITION_LENGTH: int = 10
    STREAM_TIMEOUT: int = 60
    RECOGNITION_CONFIDENCE_THRESHOLD: float = 0.7

    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FILE: str = "logs/app.log"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
