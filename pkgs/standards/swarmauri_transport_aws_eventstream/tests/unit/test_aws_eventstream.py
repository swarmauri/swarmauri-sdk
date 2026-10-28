from __future__ import annotations

from collections import deque
from types import SimpleNamespace

import pytest
from swarmauri_transport_aws_eventstream import (
    AwsEventStreamClient,
    AwsEventStreamCodec,
    AwsEventStreamConnection,
    AwsEventStreamError,
)
from swarmauri_base.transports.bidirectional.BidirectionalStreamState import (
    BidirectionalStreamState,
)
from swarmauri_core.transports.i_bidirectional_stream import (
    IBidirectionalStreamClient,
    IBidirectionalStreamConnection,
)

models = pytest.importorskip("aws_sdk_bedrock_runtime.models")
BidirectionalOutputPayloadPart = models.BidirectionalOutputPayloadPart
InvokeModelWithBidirectionalStreamOutputChunk = (
    models.InvokeModelWithBidirectionalStreamOutputChunk
)
InvokeModelWithBidirectionalStreamOutputValidationException = (
    models.InvokeModelWithBidirectionalStreamOutputValidationException
)
ValidationException = models.ValidationException


class Publisher:
    def __init__(self):
        self.events = []
        self.closed = False

    async def send(self, event):
        self.events.append(event)

    async def close(self):
        self.closed = True


class Receiver:
    def __init__(self, *events):
        self.events = deque(events)
        self.closed = False

    async def receive(self):
        return self.events.popleft() if self.events else None

    async def close(self):
        self.closed = True


class Stream:
    def __init__(self, *events):
        self.input_stream = Publisher()
        self.receiver = Receiver(*events)
        self.await_output_calls = 0
        self.close_calls = 0

    async def await_output(self):
        self.await_output_calls += 1
        return object(), self.receiver

    async def close(self):
        self.close_calls += 1
        await self.input_stream.close()
        await self.receiver.close()


def output(payload: bytes):
    return InvokeModelWithBidirectionalStreamOutputChunk(
        BidirectionalOutputPayloadPart(bytes_=payload)
    )


def _public_methods(cls):
    return {
        name
        for name, value in cls.__dict__.items()
        if not name.startswith("_")
        and name != "model_post_init"
        and (callable(value) or isinstance(value, (classmethod, staticmethod)))
    }


def test_public_method_inventory_is_exhaustive():
    assert _public_methods(AwsEventStreamCodec) == {"encode", "decode"}
    assert _public_methods(AwsEventStreamConnection) == {
        "from_stream",
        "asend",
        "areceive",
        "iter_events",
        "aiter_events",
        "aclose",
    }
    assert _public_methods(AwsEventStreamError) == set()


@pytest.mark.asyncio
async def test_connection_translates_events_and_closes():
    stream = Stream(output(b'{"event":{"textOutput":{"content":"hi"}}}'))
    connection = AwsEventStreamConnection.from_stream(stream)

    await connection.asend({"event": {"sessionStart": {}}})
    assert stream.input_stream.events[0].value.bytes_ == (
        b'{"event":{"sessionStart":{}}}'
    )
    assert await connection.areceive() == {
        "event": {"textOutput": {"content": "hi"}}
    }

    await connection.aclose()
    assert stream.input_stream.closed
    assert stream.receiver.closed
    assert connection.state == BidirectionalStreamState.CLOSED.value


def test_client_and_connection_implement_transport_interfaces():
    assert isinstance(AwsEventStreamClient(), IBidirectionalStreamClient)
    assert isinstance(
        AwsEventStreamConnection.from_stream(Stream()),
        IBidirectionalStreamConnection,
    )


@pytest.mark.asyncio
async def test_receiver_is_initialized_once_for_multiple_events():
    stream = Stream(output(b'{"sequence":1}'), output(b'{"sequence":2}'))
    connection = AwsEventStreamConnection.from_stream(stream)
    assert await connection.areceive() == {"sequence": 1}
    assert await connection.areceive() == {"sequence": 2}
    assert stream.await_output_calls == 1


@pytest.mark.asyncio
async def test_stream_end_closes_resources_once_and_blocks_io():
    stream = Stream()
    connection = AwsEventStreamConnection.from_stream(stream)
    with pytest.raises(EOFError, match="ended"):
        await connection.areceive()
    await connection.aclose()
    assert stream.close_calls == 1
    assert connection.state == BidirectionalStreamState.CLOSED.value
    with pytest.raises(RuntimeError, match="not open"):
        await connection.asend({"event": {}})
    with pytest.raises(EOFError, match="closed"):
        await connection.areceive()


@pytest.mark.asyncio
async def test_close_failure_still_reaches_terminal_state():
    class FailingStream(Stream):
        async def close(self):
            self.close_calls += 1
            raise OSError("close failed")

    stream = FailingStream()
    connection = AwsEventStreamConnection.from_stream(stream)
    with pytest.raises(OSError, match="close failed"):
        await connection.aclose()
    assert connection.state == BidirectionalStreamState.CLOSED.value
    await connection.aclose()
    assert stream.close_calls == 1


@pytest.mark.asyncio
async def test_iterator_stops_on_stream_end():
    connection = AwsEventStreamConnection.from_stream(Stream())
    assert [event async for event in connection.aiter_events()] == []


def test_sync_iterator_receives_until_stream_end():
    connection = AwsEventStreamConnection.from_stream(
        Stream(output(b'{"sequence":1}'))
    )
    assert list(connection.iter_events()) == [{"sequence": 1}]


def test_codec_maps_aws_exception_events():
    event = InvokeModelWithBidirectionalStreamOutputValidationException(
        ValidationException(message="invalid input")
    )
    with pytest.raises(AwsEventStreamError, match="invalid input"):
        AwsEventStreamCodec().decode(event)


def test_codec_encodes_bytes_without_json_wrapping():
    encoded = AwsEventStreamCodec().encode(b"raw")
    assert encoded.value.bytes_ == b"raw"


@pytest.mark.parametrize("payload", [b"", b"not-json", b"\xff"])
def test_codec_rejects_invalid_output_payload(payload):
    with pytest.raises((UnicodeDecodeError, ValueError)):
        AwsEventStreamCodec().decode(output(payload))


def test_codec_rejects_unknown_output_union_member():
    with pytest.raises(AwsEventStreamError, match="Unexpected AWS"):
        AwsEventStreamCodec().decode(SimpleNamespace(value=object()))


@pytest.mark.asyncio
async def test_client_constructs_sdk_operation_from_endpoint():
    captured = {}
    stream = Stream()

    class Client:
        def __init__(self, config):
            captured["config"] = config

        def invoke_model_with_bidirectional_stream(self, operation):
            captured["model_id"] = operation.model_id
            return stream

    client = AwsEventStreamClient(sdk_client_factory=Client)
    connection = await client.aconnect(
        "https://bedrock-runtime.us-west-2.amazonaws.com/model/"
        "amazon.nova-sonic-v1%3A0/invoke-with-bidirectional-stream",
        region="us-west-2",
        aws_access_key_id="access",
        aws_secret_access_key="secret",
    )

    assert captured["model_id"] == "amazon.nova-sonic-v1:0"
    assert captured["config"].region == "us-west-2"
    assert isinstance(connection, AwsEventStreamConnection)


@pytest.mark.asyncio
async def test_client_rejects_partial_explicit_credentials():
    client = AwsEventStreamClient()
    with pytest.raises(ValueError, match="provided together"):
        await client.aconnect(
            "https://bedrock-runtime.us-east-1.amazonaws.com",
            model_id="amazon.nova-sonic-v1:0",
            aws_access_key_id="access",
        )


@pytest.mark.asyncio
async def test_client_rejects_headers_unknown_options_and_missing_model():
    client = AwsEventStreamClient()
    endpoint = "https://bedrock-runtime.us-east-1.amazonaws.com"
    with pytest.raises(ValueError, match="Custom headers"):
        await client.aconnect(endpoint, headers={"x-test": "value"})
    with pytest.raises(TypeError, match="unknown"):
        await client.aconnect(endpoint, model_id="model", unknown=True)
    with pytest.raises(ValueError, match="model_id"):
        await client.aconnect(endpoint)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "endpoint",
    [
        "relative/path",
        "ftp://example.com/model/m/invoke-with-bidirectional-stream",
    ],
)
async def test_client_rejects_non_http_absolute_endpoints(endpoint):
    client = AwsEventStreamClient()
    with pytest.raises(ValueError, match="absolute HTTP"):
        await client.aconnect(endpoint, model_id="model")


@pytest.mark.asyncio
async def test_client_uses_profile_credentials_when_explicit_pair_absent(
    monkeypatch,
):
    captured = {}

    class Client:
        def __init__(self, config):
            captured["config"] = config

        def invoke_model_with_bidirectional_stream(self, operation):
            return Stream()

    monkeypatch.setattr(
        AwsEventStreamClient,
        "_profile_credentials",
        staticmethod(
            lambda profile: {
                "aws_access_key_id": f"{profile}-id",
                "aws_secret_access_key": "secret",
                "aws_session_token": "token",
            }
        ),
    )
    await AwsEventStreamClient(sdk_client_factory=Client).aconnect(
        "https://bedrock-runtime.us-east-1.amazonaws.com",
        model_id="model",
        profile="dev",
    )
    assert captured["config"].aws_access_key_id == "dev-id"
    assert captured["config"].aws_secret_access_key == "secret"
    assert captured["config"].aws_session_token == "token"


@pytest.mark.asyncio
async def test_sync_connect_is_rejected_inside_running_loop():
    client = AwsEventStreamClient()
    with pytest.raises(RuntimeError, match="Use aconnect"):
        client.connect(
            "https://bedrock-runtime.us-east-1.amazonaws.com",
            model_id="model",
        )
