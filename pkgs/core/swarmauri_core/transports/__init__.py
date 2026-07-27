"""Transport interfaces and shared exports for Swarmauri core."""

from .ITransport import ITransport
from .capabilities import TransportCapabilities
from .enums import (
    AddressScheme,
    Cast,
    Feature,
    IOModel,
    Protocol,
    SecurityMode,
)
from .i_anycast import IAnycastTransport
from .i_appserver import HttpApp, IAppServer
from .i_bidirectional_stream import (
    IBidirectionalStreamClient,
    IBidirectionalStreamConnection,
)
from .i_broadcast import IBroadcastTransport
from .i_http_client import IHttpClient
from .i_http_response import IHttpResponse
from .i_http_stream_response import (
    IAsyncHttpStreamResponse,
    IHttpStreamResponse,
)
from .i_multicast import IMulticastTransport
from .i_multiplex import ChannelHandle, IMultiplexTransport
from .i_peer import IPeerTransport
from .i_runnable import Handler, IRunnable, Role
from .i_unicast import IUnicastTransport
from .i_websocket_client import IWebSocketClient
from .i_websocket_connection import IWebSocketConnection, WebSocketMessage
from .i_websocket_multiplex import IWebSocketMultiplexConnection

__all__ = [
    "AddressScheme",
    "Cast",
    "ChannelHandle",
    "Feature",
    "Handler",
    "HttpApp",
    "IAnycastTransport",
    "IAppServer",
    "IAsyncHttpStreamResponse",
    "IBidirectionalStreamClient",
    "IBidirectionalStreamConnection",
    "IBroadcastTransport",
    "IHttpClient",
    "IHttpResponse",
    "IHttpStreamResponse",
    "IMulticastTransport",
    "IMultiplexTransport",
    "IOModel",
    "IPeerTransport",
    "IRunnable",
    "ITransport",
    "IUnicastTransport",
    "IWebSocketClient",
    "IWebSocketConnection",
    "IWebSocketMultiplexConnection",
    "Protocol",
    "Role",
    "SecurityMode",
    "TransportCapabilities",
    "WebSocketMessage",
]
