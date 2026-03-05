"""HTTPX transport compatibility helpers."""

from __future__ import annotations

import importlib
import importlib.util
from typing import Any


def ensure_httpx_sync_transport() -> None:
    spec = importlib.util.find_spec("httpx")
    if spec is None:
        return
    httpx = importlib.import_module("httpx")
    if hasattr(httpx.ASGITransport, "__enter__"):
        return

    def __enter__(self) -> Any:
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        return None

    httpx.ASGITransport.__enter__ = __enter__
    httpx.ASGITransport.__exit__ = __exit__
