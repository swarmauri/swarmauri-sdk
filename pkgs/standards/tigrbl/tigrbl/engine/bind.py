"""Compatibility wrappers for engine binding APIs.

Canonical collect/install APIs now live on :class:`tigrbl._concrete._engine.Engine`.
"""

from __future__ import annotations

from typing import Any, Iterable, Mapping

from .._concrete._engine import Engine


def bind(collected: Mapping[str, Any]) -> None:
    """Bind a collected configuration mapping into the resolver."""
    Engine.install_engine_bindings(collected)


def install_from_objects(
    *,
    app: Any | None = None,
    router: Any | None = None,
    tables: Iterable[Any] = (),
) -> None:
    """Collect engine config from objects and bind them to the resolver."""
    Engine.install_from_objects(app=app, router=router, tables=tables)


def collect_engine_bindings(
    *, app: Any | None = None, router: Any | None = None, tables: Iterable[Any] = ()
) -> Mapping[str, Any]:
    """Collect engine bindings from app/router/table objects."""
    return Engine.collect_engine_bindings(app=app, router=router, tables=tables)


__all__ = ["bind", "install_from_objects", "collect_engine_bindings"]
