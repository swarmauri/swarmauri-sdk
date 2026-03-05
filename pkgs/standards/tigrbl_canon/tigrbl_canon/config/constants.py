"""Compatibility constants for legacy ``tigrbl_canon.config.constants`` imports."""

from __future__ import annotations

from tigrbl.config.constants import *  # noqa: F401,F403
from tigrbl.config.constants import __all__ as _TIGRBL_ALL
from tigrbl.config.constants import CANON
from tigrbl_core.config.constants import TIGRBL_NESTED_PATHS_ATTR
from tigrbl_runtime.config.constants import CTX_SKIP_PERSIST_FLAG

__all__ = [
    *list(_TIGRBL_ALL),
    "CANON",
    "TIGRBL_NESTED_PATHS_ATTR",
    "CTX_SKIP_PERSIST_FLAG",
]
