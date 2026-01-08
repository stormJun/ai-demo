from typing import Any, AsyncGenerator, Optional

from app.config import settings
from app.utils.logger import logger


class QwenClient:
    """Qwen (通义千问) API client wrapper."""

    def __init__(self, client: Optional[Any] = None, api_key: Optional[str] = None, model: Optional[str] = None):
        self.dashscope = client
        self.api_key = api_key or settings.QWEN_API_KEY
        self.model = model or settings.QWEN_MODEL
        self._configured = False

    @staticmethod
    def _import_dashscope():
        try:
            import dashscope  # type: ignore
        except ImportError as exc:
            raise ImportError("dashscope is required, please install dependencies.") from exc
        return dashscope

    def _ensure_client(self):
        if self.dashscope is None:
            self.dashscope = self._import_dashscope()

        if not self._configured:
            try:
                self.dashscope.api_key = self.api_key  # type: ignore[attr-defined]
            except Exception:
                # Some fakes used in tests might not support attribute assignment
                pass
            self._configured = True

    async def stream_generate(self, prompt: str, system_prompt: str = "") -> AsyncGenerator[str, None]:
        """Stream content generation."""
        import asyncio

        if not self.api_key:
            raise ValueError("QWEN_API_KEY is not configured.")

        self._ensure_client()

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]

        logger.info(f"开始流式生成, 模型: {self.model}")

        try:
            response = self.dashscope.Generation.call(  # type: ignore[attr-defined]
                model=self.model,
                messages=messages,
                stream=True,
                result_format="message",
                incremental_output=True,
            )

            for chunk in response:
                if getattr(chunk, "status_code", None) == 200:
                    content = chunk.output.choices[0].message.content  # type: ignore[index]
                    if content:
                        yield content
                        # 关键：让出控制权，让FastAPI能够立即发送数据
                        await asyncio.sleep(0)
                else:
                    code = getattr(chunk, "code", "unknown")
                    message = getattr(chunk, "message", "unknown")
                    error_msg = f"API Error: {code} - {message}"
                    logger.error(error_msg)
                    raise Exception(error_msg)
        except Exception as exc:
            logger.error(f"流式生成失败: {exc}")
            raise

    async def generate(self, prompt: str, system_prompt: str = "") -> str:
        """Non-stream generation (used for recognition)."""
        if not self.api_key:
            raise ValueError("QWEN_API_KEY is not configured.")

        self._ensure_client()

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ]

        logger.info(f"开始非流式生成, 模型: {self.model}")

        try:
            response = self.dashscope.Generation.call(  # type: ignore[attr-defined]
                model=self.model,
                messages=messages,
                result_format="message",
            )

            if getattr(response, "status_code", None) == 200:
                return response.output.choices[0].message.content  # type: ignore[index]

            code = getattr(response, "code", "unknown")
            message = getattr(response, "message", "unknown")
            error_msg = f"API Error: {code} - {message}"
            logger.error(error_msg)
            raise Exception(error_msg)
        except Exception as exc:
            logger.error(f"非流式生成失败: {exc}")
            raise
