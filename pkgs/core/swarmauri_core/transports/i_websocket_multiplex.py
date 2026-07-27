"""Multiplexed WebSocket connection interface."""

from abc import ABC

from .i_multiplex import IMultiplexTransport
from .i_websocket_connection import IWebSocketConnection


class IWebSocketMultiplexConnection(
    IWebSocketConnection, IMultiplexTransport, ABC
):
    """WebSocket connection exposing independent logical channels."""
