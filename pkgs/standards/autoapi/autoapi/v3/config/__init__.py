# autoapi/v3/config/__init__.py
"""AutoAPI v3 – configuration surface.

Exports:
    - DEFAULTS: canonical configuration defaults
    - CfgView:  read-only config view (attr + dict access)
    - resolve_cfg(...): precedence-based merger across apps/api/tab/cols/op/overrides
"""

from __future__ import annotations

from .defaults import DEFAULTS
from .resolver import CfgView, resolve_cfg
from .constants import __autoapi_auth_context__

__all__ = [
    "DEFAULTS",
    "CfgView",
    "resolve_cfg",
    "__autoapi_auth_context__",
]
