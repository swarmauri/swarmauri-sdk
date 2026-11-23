from importlib import import_module
from unittest.mock import AsyncMock

import pytest
from swarmauri_base.live_models.LiveConfigBase import LiveConfigBase
from swarmauri_core.transports.i_bidirectional_stream import (
    IBidirectionalStreamClient,
)
from swarmauri_live_model_amazon_nova import NovaSonicLiveModel
from swarmauri_provider_amazon_nova import AmazonNovaProvider


@pytest.mark.asyncio
async def test_model_uses_prepared_aws_eventstream_connection(monkeypatch):
    calls = []

    class Transport(IBidirectionalStreamClient):
        def connect(self, endpoint, *, headers=None, **kwargs):
            raise NotImplementedError

        async def aconnect(self, endpoint, **kwargs):
            calls.append((endpoint, kwargs))
            return object()

    module = import_module(
        "swarmauri_live_model_amazon_nova.NovaSonicLiveModel"
    )
    monkeypatch.setattr(
        module.NovaSonicLiveSession,
        "create",
        AsyncMock(return_value=object()),
    )
    model = NovaSonicLiveModel(
        provider=AmazonNovaProvider(
            region="us-west-2",
            access_key_id="access",
            secret_access_key="secret",
        ),
        transport=Transport(),
    )

    await model.aconnect(LiveConfigBase())

    endpoint, options = calls[0]
    assert endpoint.startswith(
        "https://bedrock-runtime.us-west-2.amazonaws.com/model/"
    )
    assert endpoint.endswith("/invoke-with-bidirectional-stream")
    assert options["model_id"] == "amazon.nova-sonic-v1:0"
    assert options["region"] == "us-west-2"
    assert options["aws_access_key_id"] == "access"
    assert options["aws_secret_access_key"] == "secret"
