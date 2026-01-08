import json
from datetime import datetime

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from app.config import settings
from app.models.schemas import HealthResponse, RecognitionRequest, TranslateRequest
from app.services.recognition import RecognitionService
from app.services.translation import TranslationService
from app.utils.logger import logger

router = APIRouter(prefix="/api", tags=["API"])

translation_service = TranslationService()
recognition_service = RecognitionService()


@router.post("/translate/stream")
async def translate_stream(request: TranslateRequest):
    """Streaming translation endpoint (SSE)."""

    async def generate():
        try:
            async for chunk in translation_service.translate_stream(request.content, request.direction):
                data = json.dumps({"type": "content", "data": chunk}, ensure_ascii=False)
                yield f"data: {data}\n\n"

            done = json.dumps({"type": "done", "data": ""})
            yield f"data: {done}\n\n"
        except Exception as exc:  # pylint: disable=broad-except
            logger.error(f"翻译失败: {exc}")
            error = json.dumps({"type": "error", "data": f"翻译失败: {exc}"}, ensure_ascii=False)
            yield f"data: {error}\n\n"

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "Connection": "keep-alive"},
    )


@router.post("/recognize")
async def recognize(request: RecognitionRequest):
    """Recognize scene type."""
    try:
        return await recognition_service.recognize(request.content)
    except Exception as exc:  # pylint: disable=broad-except
        logger.error(f"识别失败: {exc}")
        raise HTTPException(status_code=500, detail=f"识别失败: {exc}") from exc


@router.get("/health")
async def health_check() -> HealthResponse:
    """Health check."""
    return HealthResponse(
        status="ok",
        timestamp=datetime.now().isoformat(),
        api_key_configured=bool(settings.QWEN_API_KEY),
    )

