"""Shared WebSocket client configuration."""

from abc import ABC

from pydantic import ConfigDict, Field
from swarmauri_core.transports.i_websocket_client import IWebSocketClient

from swarmauri_base.ComponentBase import ComponentBase


class WebSocketClientBase(IWebSocketClient, ComponentBase, ABC):
    timeout: float = Field(default=60.0, gt=0)
    ping_interval: float = Field(default=20.0, gt=0)
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")
