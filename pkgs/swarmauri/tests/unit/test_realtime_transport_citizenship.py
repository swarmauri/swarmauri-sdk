from swarmauri.plugin_citizenship_registry import PluginCitizenshipRegistry


def test_realtime_transport_citizenship():
    registry = PluginCitizenshipRegistry.SECOND_CLASS_REGISTRY
    assert registry["swarmauri.transports.HttpxClient"] == (
        "swarmauri_transport_httpx.HttpxClient"
    )
    assert registry["swarmauri.transports.WebSocketClient"] == (
        "swarmauri_transport_websocket.WebSocketClient"
    )
