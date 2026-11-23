"""SDK-independent coverage for asynchronous stream creation."""

from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from swarmauri_transport_aws_eventstream import AwsEventStreamClient


@pytest.mark.asyncio
@pytest.mark.parametrize("injected", [False, True])
async def test_async_stream_operation_is_awaited(monkeypatch, injected):
    stream = SimpleNamespace(input_stream=SimpleNamespace(send=AsyncMock()))
    operation = AsyncMock(return_value=stream)
    sdk_client = SimpleNamespace(
        invoke_model_with_bidirectional_stream=operation
    )

    def factory(config):
        return sdk_client

    monkeypatch.setattr(
        AwsEventStreamClient,
        "_default_sdk",
        staticmethod(lambda: (factory, SimpleNamespace, SimpleNamespace)),
    )
    client = AwsEventStreamClient(
        sdk_client_factory=factory if injected else None
    )
    connection = await client.aconnect("https://example.com", model_id="model")
    operation.assert_awaited_once()
    assert operation.call_args.args[0].model_id == "model"
    monkeypatch.setattr(
        type(connection._codec), "encode", lambda self, event: event
    )
    await connection.asend({"event": {"sessionStart": {}}})
    stream.input_stream.send.assert_awaited_once()


@pytest.mark.asyncio
async def test_async_stream_open_error_propagates(monkeypatch):
    operation = AsyncMock(side_effect=RuntimeError("stream rejected"))
    monkeypatch.setattr(
        AwsEventStreamClient,
        "_default_sdk",
        staticmethod(
            lambda: (
                lambda config: SimpleNamespace(
                    invoke_model_with_bidirectional_stream=operation
                ),
                SimpleNamespace,
                SimpleNamespace,
            )
        ),
    )
    with pytest.raises(RuntimeError, match="stream rejected"):
        await AwsEventStreamClient().aconnect(
            "https://example.com", model_id="model"
        )
    operation.assert_awaited_once()
