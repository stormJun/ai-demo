from typing import AsyncGenerator, Optional

from app.config import settings
from app.prompts import dev_to_product, product_to_dev
from app.services.ai_client import QwenClient
from app.utils.logger import logger


class TranslationService:
    """Translation service."""

    def __init__(self, ai_client: Optional[QwenClient] = None):
        self.ai_client = ai_client or QwenClient()

    async def translate_stream(self, content: str, direction: str) -> AsyncGenerator[str, None]:
        """Translate content with streaming output."""
        if len(content) > settings.MAX_INPUT_LENGTH:
            raise ValueError("输入内容过长")

        logger.info(f"开始翻译, 方向: {direction}, 内容长度: {len(content)}")

        if direction == "product_to_dev":
            prompt = product_to_dev.build_prompt(content)
            system_prompt = product_to_dev.SYSTEM_PROMPT
        elif direction == "dev_to_product":
            prompt = dev_to_product.build_prompt(content)
            system_prompt = dev_to_product.SYSTEM_PROMPT
        else:
            raise ValueError("不支持的翻译方向")

        async for chunk in self.ai_client.stream_generate(prompt, system_prompt):
            if not chunk:
                continue
            for ch in chunk:
                yield ch

        logger.info("翻译完成")
