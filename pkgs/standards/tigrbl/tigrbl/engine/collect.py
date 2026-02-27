"""Compatibility wrapper for engine collection APIs.

Canonical collection now lives on :class:`tigrbl._concrete._engine.Engine`.
"""

from __future__ import annotations

from .._concrete._engine import Engine


def collect_engine_config(*, app=None, router=None, tables=()):
    return Engine.collect_engine_bindings(app=app, router=router, tables=tables)


__all__ = ["collect_engine_config"]
