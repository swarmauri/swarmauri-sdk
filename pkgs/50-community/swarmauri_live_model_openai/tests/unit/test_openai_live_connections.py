from importlib import import_module
from unittest.mock import AsyncMock

import pytest
from swarmauri_base.live_models.LiveConfigBase import LiveConfigBase
from swarmauri_live_model_openai import (
    OpenAIRealtimeModel,
    OpenAIResponsesWSModel,
)
from swarmauri_provider_openai import OpenAIProvider


class RecordingTransport:
    def __init__(self):
        self.calls = []

    async def aconnect(self, url, **kwargs):
        self.calls.append((url, kwargs))
        return object()


@pytest.mark.asyncio
async def test_realtime_uses_prepared_provider_connection(monkeypatch):
    transport = RecordingTransport()

    module = import_module("swarmauri_live_model_openai.OpenAIRealtimeModel")
    monkeypatch.setattr(
        module.OpenAIRealtimeSession,
        "create",
        AsyncMock(return_value=object()),
    )
    model = OpenAIRealtimeModel(
        provider=OpenAIProvider(api_key="secret"), transport=transport
    )
    await model.aconnect(LiveConfigBase())

    url, kwargs = transport.calls[0]
    assert url.endswith("?model=gpt-realtime")
    assert kwargs["headers"]["Authorization"] == "Bearer secret"
    assert kwargs["headers"]["OpenAI-Beta"] == "realtime=v1"


@pytest.mark.asyncio
async def test_responses_uses_prepared_provider_connection(monkeypatch):
    transport = RecordingTransport()

    module = import_module(
        "swarmauri_live_model_openai.OpenAIResponsesWSModel"
    )
    monkeypatch.setattr(
        module.OpenAIRealtimeSession,
        "create",
        AsyncMock(return_value=object()),
    )
    model = OpenAIResponsesWSModel(
        provider=OpenAIProvider(api_key="secret"), transport=transport
    )
    await model.aconnect(LiveConfigBase())

    url, kwargs = transport.calls[0]
    assert url == "wss://api.openai.com/v1/responses"
    assert kwargs["headers"]["Authorization"] == "Bearer secret"
