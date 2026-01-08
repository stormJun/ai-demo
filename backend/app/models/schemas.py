from datetime import datetime
from typing import Literal, Optional

from pydantic import BaseModel, Field


class TranslateRequest(BaseModel):
    """Translation request."""

    content: str = Field(..., min_length=1, max_length=5000, description="待翻译内容")
    direction: Literal["product_to_dev", "dev_to_product"] = Field(..., description="翻译方向")

    model_config = {
        "json_schema_extra": {
            "example": {"content": "我们需要一个智能推荐功能", "direction": "product_to_dev"}
        }
    }


class StreamChunk(BaseModel):
    """Streaming response chunk."""

    type: Literal["content", "done", "error"]
    data: str


class RecognitionRequest(BaseModel):
    """Scene recognition request."""

    content: str = Field(..., min_length=10, description="待识别内容")


class RecognitionResponse(BaseModel):
    """Scene recognition response."""

    scene: Literal["product_requirement", "tech_solution", "uncertain"]
    confidence: float = Field(..., ge=0, le=1)
    reason: Optional[str] = None
    suggested_direction: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    timestamp: str
    api_key_configured: bool

