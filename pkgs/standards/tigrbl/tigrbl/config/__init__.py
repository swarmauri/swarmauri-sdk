# tigrbl/config/__init__.py
"""Tigrbl – configuration surface.

Exports:
    - DEFAULTS: canonical configuration defaults
    - CfgView:  read-only config view (attr + dict access)
<<<<<<< HEAD
    - resolve_cfg(...): precedence-based merger across apps/routers/tab/cols/op/overrides
=======
    - resolve_cfg(...): precedence-based merger across apps/router/tab/cols/op/overrides
>>>>>>> a8f183f2e9f9d711015dec095ba64838fae67a3c
"""

from __future__ import annotations

from .defaults import DEFAULTS
from .resolver import CfgView, resolve_cfg

__all__ = [
    "DEFAULTS",
    "CfgView",
    "resolve_cfg",
]
