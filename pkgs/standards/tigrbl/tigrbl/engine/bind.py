"""Compatibility wrappers for engine binding APIs.

Canonical collect/install traversal now lives in ``tigrbl.mapping.traversal``.
"""

from __future__ import annotations

from typing import Any, Iterable, Mapping

from ..mapping.traversal import (
    collect_engine_bindings,
    install_engine_bindings,
    install_from_objects as _install_from_objects,
)


def bind(collected: Mapping[str, Any]) -> None:
    """Bind a collected configuration mapping into the resolver."""
    install_engine_bindings(collected)


def install_from_objects(
    *,
    app: Any | None = None,
    router: Any | None = None,
    tables: Iterable[Any] = (),
) -> None:
    """Collect engine config from objects and bind them to the resolver."""
    _install_from_objects(app=app, router=router, tables=tables)


__all__ = ["bind", "install_from_objects", "collect_engine_bindings"]
