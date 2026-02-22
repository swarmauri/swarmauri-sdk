"""Compatibility wrappers for transport gateway adapters."""

from __future__ import annotations

from tigrbl.transport.gw import asgi_app, wsgi_app

__all__ = ["asgi_app", "wsgi_app"]
