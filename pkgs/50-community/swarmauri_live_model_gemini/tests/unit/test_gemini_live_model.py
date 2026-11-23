from importlib import import_module
from unittest.mock import AsyncMock

import pytest
from swarmauri_base.live_models.LiveConfigBase import LiveConfigBase
from swarmauri_live_model_gemini import GeminiLiveModel
from swarmauri_provider_gemini import GeminiProvider


def test_model_capabilities():
    model = GeminiLiveModel()
    assert "video" in model.capabilities.input_modalities
    assert "audio" in model.capabilities.output_modalities


@pytest.mark.asyncio
async def test_model_uses_prepared_query_auth(monkeypatch):
    calls = []

    class Transport:
        async def aconnect(self, url, **kwargs):
            calls.append((url, kwargs))
            return object()

    module = import_module("swarmauri_live_model_gemini.GeminiLiveModel")
    monkeypatch.setattr(
        module.GeminiLiveSession,
        "create",
        AsyncMock(return_value=object()),
    )
    model = GeminiLiveModel(
        provider=GeminiProvider(api_key="a key"), transport=Transport()
    )
    await model.aconnect(LiveConfigBase())

    assert calls[0][0].endswith("?key=a+key")
    assert calls[0][1]["headers"] == {}
