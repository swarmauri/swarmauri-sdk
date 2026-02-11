from __future__ import annotations

from typing import Any


def mount_openapi(*args: Any, **kwargs: Any) -> Any:
    from .openapi import mount_openapi as _mount_openapi

    return _mount_openapi(*args, **kwargs)


def mount_swagger(*args: Any, **kwargs: Any) -> Any:
    from .swagger import mount_swagger as _mount_swagger

    return _mount_swagger(*args, **kwargs)


def mount_lens(*args: Any, **kwargs: Any) -> Any:
    from .lens import mount_lens as _mount_lens

    return _mount_lens(*args, **kwargs)


def mount_openrpc(*args: Any, **kwargs: Any) -> Any:
    from .openrpc import mount_openrpc as _mount_openrpc

    return _mount_openrpc(*args, **kwargs)


def build_openrpc_spec(*args: Any, **kwargs: Any) -> Any:
    from .openrpc import build_openrpc_spec as _build_openrpc_spec

    return _build_openrpc_spec(*args, **kwargs)


__all__ = [
    "build_openrpc_spec",
    "mount_lens",
    "mount_openapi",
    "mount_openrpc",
    "mount_swagger",
]
