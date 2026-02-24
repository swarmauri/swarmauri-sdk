"""
h2/__init__.py

This package provides foundational support for HTTP/2 including:
- Frame formatting and parsing
- HPACK header compression/decompression
- Multiplexing and stream management
- Flow control handling
"""

from .frames import (
    HTTP2Frame,
    DATA,
    HEADERS,
    PRIORITY,
    RST_STREAM,
    SETTINGS,
    PUSH_PROMISE,
    PING,
    GOAWAY,
    WINDOW_UPDATE,
    CONTINUATION,
)
from .hpack import hpack_encode, hpack_decode
from .multiplex import HTTP2Multiplexer
from .flow_control import FlowControlManager

__all__ = [
    "HTTP2Frame",
    "DATA",
    "HEADERS",
    "PRIORITY",
    "RST_STREAM",
    "SETTINGS",
    "PUSH_PROMISE",
    "PING",
    "GOAWAY",
    "WINDOW_UPDATE",
    "CONTINUATION",
    "hpack_encode",
    "hpack_decode",
    "HTTP2Multiplexer",
    "FlowControlManager",
]
