import pytest

from app.prompts import product_to_dev
from app.services.translation import TranslationService


def test_prompt_building():
    content = "我们需要一个推荐功能"
    prompt = product_to_dev.build_prompt(content)
    assert "产品需求" in prompt
    assert content in prompt


class _FakeAIClient:
    async def stream_generate(self, prompt: str, system_prompt: str = ""):
        yield "片段1"
        yield "片段2"


@pytest.mark.asyncio
async def test_translation_service_stream():
    service = TranslationService(ai_client=_FakeAIClient())
    chunks = []
    async for chunk in service.translate_stream("测试内容", "product_to_dev"):
        chunks.append(chunk)
    assert "".join(chunks) == "片段1片段2"
