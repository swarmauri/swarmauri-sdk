"""ASGI application entrypoint for the cron API."""

from __future__ import annotations

from .api import build_app

app = build_app(async_mode=True)

__all__ = ["app", "build_app"]
