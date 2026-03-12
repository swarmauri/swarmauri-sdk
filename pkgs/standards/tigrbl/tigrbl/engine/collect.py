"""Compatibility wrapper for engine collection APIs.

Canonical collect traversal now lives in ``tigrbl.mapping.traversal``.
"""

from __future__ import annotations

from tigrbl_canon.mapping.traversal import collect_engine_bindings as collect_engine_config

__all__ = ["collect_engine_config"]
