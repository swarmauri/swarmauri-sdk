from unittest.mock import AsyncMock

from swarmauri_base.transports.bidirectional.BidirectionalStreamClientBase import (  # noqa: E501
    BidirectionalStreamClientBase,
)
from swarmauri_tests_component import ComponentSpec, MethodSpec
from swarmauri_transport_aws_eventstream import AwsEventStreamClient


def _connect(client):
    client.aconnect = AsyncMock(return_value="connection")
    assert (
        client.connect("https://example.com", model_id="model") == "connection"
    )


async def _aconnect(client):
    captured = {}

    class Config:
        def __init__(self, **kwargs):
            captured["config"] = kwargs

    class Input:
        def __init__(self, model_id):
            self.model_id = model_id

    class Stream:
        pass

    class Client:
        def __init__(self, config):
            pass

        def invoke_model_with_bidirectional_stream(self, operation):
            captured["model"] = operation.model_id
            return Stream()

    client.sdk_client_factory = Client
    client._default_sdk = lambda: (Client, Config, Input)
    connection = await client.aconnect(
        "https://example.com/model/test/invoke-with-bidirectional-stream"
    )
    assert connection.state == "open"
    assert captured["model"] == "test"


def pytest_swarmauri_component_specs():
    return [
        ComponentSpec(
            AwsEventStreamClient,
            {},
            "Transport",
            None,
            BidirectionalStreamClientBase,
            excluded_fields=("sdk_client_factory",),
            method_specs=(
                MethodSpec("connect", _connect),
                MethodSpec("aconnect", _aconnect),
            ),
        )
    ]
