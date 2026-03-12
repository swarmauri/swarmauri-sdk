# tigrbl/config/__init__.py
"""Tigrbl – configuration surface.

Exports:
    - DEFAULTS: canonical configuration defaults
    - CfgView:  read-only config view (attr + dict access)
    - resolve_cfg(...): precedence-based merger across apps/routers/tab/cols/op/overrides
"""

from __future__ import annotations

from .defaults import DEFAULTS
from tigrbl_canon.mapping.config_resolver import CfgView, resolve_cfg

__all__ = [
    "DEFAULTS",
    "CfgView",
    "resolve_cfg",
]
