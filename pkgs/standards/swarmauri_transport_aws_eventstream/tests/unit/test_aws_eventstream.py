from __future__ import annotations

from collections import deque

import pytest
from swarmauri_transport_aws_eventstream import (
    AwsEventStreamClient,
    AwsEventStreamCodec,
    AwsEventStreamConnection,
    AwsEventStreamError,
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

    async def await_output(self):
        return object(), self.receiver

    async def close(self):
        await self.input_stream.close()
        await self.receiver.close()


def output(payload: bytes):
    return InvokeModelWithBidirectionalStreamOutputChunk(
        BidirectionalOutputPayloadPart(bytes_=payload)
    )


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


@pytest.mark.asyncio
async def test_iterator_stops_on_stream_end():
    connection = AwsEventStreamConnection.from_stream(Stream())
    assert [event async for event in connection.aiter_events()] == []


def test_codec_maps_aws_exception_events():
    event = InvokeModelWithBidirectionalStreamOutputValidationException(
        ValidationException(message="invalid input")
    )
    with pytest.raises(AwsEventStreamError, match="invalid input"):
        AwsEventStreamCodec().decode(event)


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
