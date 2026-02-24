"""Backwards-compatible middleware spec import path."""

from ..specs.middleware_spec import (
    ASGIApp,
    ASGIReceive,
    ASGISend,
    Message,
    MiddlewareSpec,
    Receive,
    Scope,
    Send,
    WSGIApp,
    WSGIStartResponse,
)

__all__ = [
    "Message",
    "Scope",
    "ASGIReceive",
    "ASGISend",
    "Receive",
    "Send",
    "ASGIApp",
    "WSGIStartResponse",
    "WSGIApp",
    "MiddlewareSpec",
]
