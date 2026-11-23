from importlib import import_module
from unittest.mock import AsyncMock

import pytest
from swarmauri_base.live_models.LiveConfigBase import LiveConfigBase
from swarmauri_live_model_qwen import QwenOmniRealtimeModel
from swarmauri_provider_qwen import QwenProvider


@pytest.mark.asyncio
async def test_model_uses_prepared_provider_connection(monkeypatch):
    calls = []

    class Transport:
        async def aconnect(self, url, **kwargs):
            calls.append((url, kwargs))
            return object()

    module = import_module("swarmauri_live_model_qwen.QwenOmniRealtimeModel")
    monkeypatch.setattr(
        module.QwenOmniRealtimeSession,
        "create",
        AsyncMock(return_value=object()),
    )
    model = QwenOmniRealtimeModel(
        provider=QwenProvider(api_key="secret"), transport=Transport()
    )
    await model.aconnect(LiveConfigBase())

    assert calls[0][0].startswith("wss://")
    assert calls[0][1]["headers"]["Authorization"] == "Bearer secret"
