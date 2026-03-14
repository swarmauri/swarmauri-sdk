from __future__ import annotations

from typing import Any


def register_runtime_route(app: Any, route: Any) -> None:
    """Compatibility shim for legacy imports.

    Runtime route metadata registration is implemented in
    ``tigrbl_concrete._concrete.runtime_route_binding``.
    """

    from tigrbl_concrete._concrete.runtime_route_binding import (
        register_runtime_route as _register_runtime_route,
    )

    _register_runtime_route(app, route)


__all__ = ["register_runtime_route"]
