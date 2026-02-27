"""Compatibility wrappers for engine binding APIs.

Canonical collect/install traversal now lives in ``tigrbl.mapping.traversal``.
"""

from __future__ import annotations

from typing import Any, Iterable, Mapping

from .._concrete._engine import Engine


def collect_engine_bindings(
    *, app: Any | None = None, router: Any | None = None, tables: Iterable[Any] = ()
) -> dict[str, Any]:
    """Collect engine configuration from first-class objects."""
    return Engine.collect_bindings(app=app, router=router, tables=tuple(tables))


def bind(collected: Mapping[str, Any]) -> None:
    """Bind a collected configuration mapping into the resolver."""
    Engine.install_bindings(dict(collected))


def install_from_objects(
    *,
    app: Any | None = None,
    router: Any | None = None,
    tables: Iterable[Any] = (),
) -> None:
    """Collect engine config from objects and bind them to the resolver."""
    Engine.install_from_objects(app=app, router=router, tables=tuple(tables))


__all__ = ["collect_engine_bindings", "bind", "install_from_objects"]
