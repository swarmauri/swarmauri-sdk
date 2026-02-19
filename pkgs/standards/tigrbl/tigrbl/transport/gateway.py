"""Transport gateway adapters for ASGI and WSGI."""

from __future__ import annotations

from ..app.transport import asgi_app, wsgi_app

__all__ = ["asgi_app", "wsgi_app"]
