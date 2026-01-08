import pytest

from app.services.recognition import RecognitionService


class _FakeAIClient:
    async def generate(self, prompt: str, system_prompt: str = "") -> str:
        return '{"scene": "product_requirement", "confidence": 0.8, "reason": "包含需求词"}'


@pytest.mark.asyncio
async def test_recognition_service():
    service = RecognitionService(ai_client=_FakeAIClient())
    result = await service.recognize("我们需要一个新的登录流程")
    assert result.scene == "product_requirement"
    assert result.suggested_direction == "product_to_dev"
    assert result.reason == "包含需求词"


@pytest.mark.asyncio
async def test_recognition_short_content():
    service = RecognitionService(ai_client=_FakeAIClient())
    result = await service.recognize("太短")
    assert result.scene == "uncertain"
    assert result.suggested_direction is None

