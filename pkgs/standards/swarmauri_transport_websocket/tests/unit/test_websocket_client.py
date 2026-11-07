from swarmauri_transport_websocket import WebSocketClient, WebSocketConnection


def test_transport_classes_are_concrete():
    assert not WebSocketClient.__abstractmethods__
    assert not WebSocketConnection.__abstractmethods__
