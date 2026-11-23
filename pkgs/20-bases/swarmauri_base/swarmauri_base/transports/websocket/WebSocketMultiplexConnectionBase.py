"""Base for genuine channel-multiplexed WebSocket protocols."""

from abc import ABC

from swarmauri_core.transports.i_websocket_multiplex import (
    IWebSocketMultiplexConnection,
)

from .WebSocketConnectionBase import WebSocketConnectionBase


class WebSocketMultiplexConnectionBase(
    WebSocketConnectionBase, IWebSocketMultiplexConnection, ABC
):
    pass
