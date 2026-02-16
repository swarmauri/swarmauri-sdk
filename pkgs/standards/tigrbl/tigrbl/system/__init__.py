# tigrbl/v3/system/__init__.py
"""Tigrbl v3 – System helpers."""

from __future__ import annotations

from pathlib import Path
from typing import Any

FAVICON_PATH = Path(__file__).parent / "favicon" / "assets" / "favicon.svg"


def mount_diagnostics(*args: Any, **kwargs: Any) -> Any:
    from .diagnostics import mount_diagnostics as _mount_diagnostics

    return _mount_diagnostics(*args, **kwargs)


def build_openapi(*args: Any, **kwargs: Any) -> Any:
    from .docs import build_openapi as _build_openapi

    return _build_openapi(*args, **kwargs)


def build_swagger(*args: Any, **kwargs: Any) -> Any:
    from .docs import build_swagger as _build_swagger

    return _build_swagger(*args, **kwargs)


def build_lens(*args: Any, **kwargs: Any) -> Any:
    from .docs import build_lens as _build_lens

    return _build_lens(*args, **kwargs)


def mount_openapi(*args: Any, **kwargs: Any) -> Any:
    from .docs import mount_openapi as _mount_openapi

    return _mount_openapi(*args, **kwargs)


def mount_swagger(*args: Any, **kwargs: Any) -> Any:
    from .docs import mount_swagger as _mount_swagger

    return _mount_swagger(*args, **kwargs)


def mount_lens(*args: Any, **kwargs: Any) -> Any:
    from .docs import mount_lens as _mount_lens

    return _mount_lens(*args, **kwargs)


def mount_openrpc(*args: Any, **kwargs: Any) -> Any:
    from .docs import mount_openrpc as _mount_openrpc

    return _mount_openrpc(*args, **kwargs)


def build_openrpc_spec(*args: Any, **kwargs: Any) -> Any:
    from .docs import build_openrpc_spec as _build_openrpc_spec

    return _build_openrpc_spec(*args, **kwargs)


def favicon_endpoint(*args: Any, **kwargs: Any) -> Any:
    from .favicon import favicon_endpoint as _favicon_endpoint

    return _favicon_endpoint(*args, **kwargs)


def mount_favicon(*args: Any, **kwargs: Any) -> Any:
    from .favicon import mount_favicon as _mount_favicon

    return _mount_favicon(*args, **kwargs)


def stop_uvicorn_server(*args: Any, **kwargs: Any) -> Any:
    from .uvicorn import stop_uvicorn_server as _stop_uvicorn_server

    return _stop_uvicorn_server(*args, **kwargs)


__all__ = [
    "build_lens",
    "build_openapi",
    "build_openrpc_spec",
    "build_swagger",
    "FAVICON_PATH",
    "favicon_endpoint",
    "mount_diagnostics",
    "mount_favicon",
    "mount_lens",
    "mount_openapi",
    "mount_openrpc",
    "mount_swagger",
    "stop_uvicorn_server",
]
