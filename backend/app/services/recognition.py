import json
from typing import Optional

from app.config import settings
from app.models.schemas import RecognitionResponse
from app.prompts import recognition
from app.services.ai_client import QwenClient
from app.utils.logger import logger


class RecognitionService:
    """Scene recognition service."""

    def __init__(self, ai_client: Optional[QwenClient] = None):
        self.ai_client = ai_client or QwenClient()

    async def recognize(self, content: str) -> RecognitionResponse:
        """Recognize whether input is product requirement or tech solution."""
        logger.info(f"开始场景识别, 内容长度: {len(content)}")

        if len(content) < settings.MIN_RECOGNITION_LENGTH:
            logger.warning("内容太短,无法识别")
            return RecognitionResponse(scene="uncertain", confidence=0.0, reason=None, suggested_direction=None)

        prompt = recognition.build_prompt(content)
        system_prompt = recognition.SYSTEM_PROMPT

        try:
            result = await self.ai_client.generate(prompt, system_prompt)
            logger.info(f"AI识别结果: {result}")

            data = json.loads(result)
            scene = data.get("scene", "uncertain")
            confidence = float(data.get("confidence", 0.0))
            reason = data.get("reason")

            threshold = settings.RECOGNITION_CONFIDENCE_THRESHOLD
            if scene == "product_requirement" and confidence > threshold:
                suggested_direction = "product_to_dev"
            elif scene == "tech_solution" and confidence > threshold:
                suggested_direction = "dev_to_product"
            else:
                suggested_direction = None

            logger.info(f"场景: {scene}, 置信度: {confidence}, 理由: {reason}, 建议方向: {suggested_direction}")

            return RecognitionResponse(
                scene=scene,
                confidence=confidence,
                reason=reason,
                suggested_direction=suggested_direction,
            )
        except json.JSONDecodeError as exc:
            logger.error(f"JSON解析失败: {exc}")
            return RecognitionResponse(scene="uncertain", confidence=0.0, reason="parse_error", suggested_direction=None)
        except Exception as exc:
            logger.error(f"场景识别失败: {exc}")
            raise
