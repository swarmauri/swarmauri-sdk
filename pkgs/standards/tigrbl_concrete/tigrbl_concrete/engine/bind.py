"""Compatibility wrappers for engine binding APIs.

Canonical collect/install traversal now lives in ``tigrbl_concrete._mapping.traversal``.
"""

from __future__ import annotations

from typing import Any, Iterable, Mapping

from tigrbl_concrete._concrete._engine import Engine


def collect(
    *, app: Any | None = None, router: Any | None = None, tables: Iterable[Any] = ()
) -> dict[str, Any]:
    """Collect engine configuration from first-class objects."""
    return Engine.collect(app=app, router=router, tables=tuple(tables))


def install(collected: Mapping[str, Any]) -> None:
    """Install a collected configuration mapping into the resolver."""
    Engine.install(dict(collected))


def collect_engine_bindings(
    *, app: Any | None = None, router: Any | None = None, tables: Iterable[Any] = ()
) -> dict[str, Any]:
    """Backward-compatible alias for :func:`collect`."""
    return collect(app=app, router=router, tables=tables)


def bind(collected: Mapping[str, Any]) -> None:
    """Backward-compatible alias for :func:`install`."""
    install(collected)


def install_from_objects(
    *,
    app: Any | None = None,
    router: Any | None = None,
    tables: Iterable[Any] = (),
) -> None:
    """Collect engine config from objects and bind them to the resolver."""
    Engine.install_from_objects(app=app, router=router, tables=tuple(tables))


__all__ = [
    "collect",
    "install",
    "collect_engine_bindings",
    "bind",
    "install_from_objects",
]
