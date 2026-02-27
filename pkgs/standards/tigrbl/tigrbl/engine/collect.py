"""Compatibility wrapper for engine collection APIs.

Canonical collect traversal now lives on ``tigrbl._concrete._engine``.
"""

from __future__ import annotations

from .._concrete._engine import collect_engine_bindings as collect_engine_config

__all__ = ["collect_engine_config"]
