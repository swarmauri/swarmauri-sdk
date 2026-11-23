import pytest

from swarmauri.plugin_citizenship_registry import PluginCitizenshipRegistry


@pytest.mark.parametrize(
    ("public_name", "target"),
    [
        ("HttpxClient", "swarmauri_transport_httpx.HttpxClient"),
        ("WebSocketClient", "swarmauri_transport_websocket.WebSocketClient"),
        (
            "AwsEventStreamClient",
            "swarmauri_transport_aws_eventstream.AwsEventStreamClient",
        ),
    ],
)
def test_realtime_transport_citizenship(public_name, target):
    registry = PluginCitizenshipRegistry.SECOND_CLASS_REGISTRY
    assert registry[f"swarmauri.transports.{public_name}"] == target
