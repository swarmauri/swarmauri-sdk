"""Backward-compatible request adapter exports."""

from __future__ import annotations

from .._concrete._request_adapters import request_from_asgi, request_from_wsgi

__all__ = ["request_from_asgi", "request_from_wsgi"]
