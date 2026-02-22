"""Backward-compatible request adapter exports.

Transport adapters now live under :mod:`tigrbl.transport`.
"""

from __future__ import annotations

from ..transport.request_adapters import request_from_asgi, request_from_wsgi

__all__ = ["request_from_asgi", "request_from_wsgi"]
