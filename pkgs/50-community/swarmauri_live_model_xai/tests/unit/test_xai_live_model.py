from importlib import import_module
from unittest.mock import AsyncMock

import pytest
from swarmauri_base.live_models.LiveConfigBase import LiveConfigBase
from swarmauri_live_model_xai import XAIRealtimeModel
from swarmauri_provider_xai import XAIProvider


@pytest.mark.asyncio
async def test_model_uses_prepared_provider_connection(monkeypatch):
    calls = []

    class Transport:
        async def aconnect(self, url, **kwargs):
            calls.append((url, kwargs))
            return object()

    module = import_module("swarmauri_live_model_xai.XAIRealtimeModel")
    monkeypatch.setattr(
        module.XAIRealtimeSession,
        "create",
        AsyncMock(return_value=object()),
    )
    model = XAIRealtimeModel(
        provider=XAIProvider(api_key="secret"), transport=Transport()
    )
    await model.aconnect(LiveConfigBase())

    assert calls[0][0] == "wss://api.x.ai/v1/realtime"
    assert calls[0][1]["headers"]["Authorization"] == "Bearer secret"
