"""Compatibility exports for middleware primitives."""

from __future__ import annotations

from .middlewares import (
    ASGIApp,
    ASGIReceive,
    ASGISend,
    BaseHTTPMiddleware,
    CORSMiddleware,
    Middleware,
    MiddlewareConfig,
    MiddlewareSpec,
    WSGIApp,
    WSGIStartResponse,
    apply_middlewares,
    middleware,
    middlewares,
)

__all__ = [
    "ASGIApp",
    "ASGIReceive",
    "ASGISend",
    "WSGIApp",
    "WSGIStartResponse",
    "MiddlewareSpec",
    "Middleware",
    "BaseHTTPMiddleware",
    "MiddlewareConfig",
    "middleware",
    "middlewares",
    "apply_middlewares",
    "CORSMiddleware",
]
