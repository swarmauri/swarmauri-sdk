"""Backward-compatible gateway exports.

Prefer importing from :mod:`tigrbl.transport.gw` for the explicit gateway contract.
"""

from __future__ import annotations

from .gw import asgi_app, wsgi_app

__all__ = ["asgi_app", "wsgi_app"]
