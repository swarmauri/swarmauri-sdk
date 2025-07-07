"""
Public façade for all table classes.

Usage
-----
    from autoapi.v2.tables import Tenant, User, Group
"""

import importlib
import sys
from typing import TYPE_CHECKING, Any
from ._base import Base

__all__ = ["Tenant", "User", "Group", "Base"]

# ------------------------------------------------------------------ #
# Lazy attribute loader (PEP 562). Keeps import graphs light-weight.
# ------------------------------------------------------------------ #
_module_map = {name: f"{__name__}.{name.lower()}" for name in __all__}

def __getattr__(name: str) -> Any:                # noqa: D401
    """Dynamically import `tenant`, `user`, or `group` on first use."""
    if name not in _module_map:
        raise AttributeError(name)
    module = importlib.import_module(_module_map[name])
    obj = getattr(module, name)
    globals()[name] = obj      # cache for future look-ups
    return obj

# ------------------------------------------------------------------ #
# Static typing support – imported eagerly only during type checking.
# ------------------------------------------------------------------ #
if TYPE_CHECKING:                           # pragma: no cover
    from ._base import Base
    from .tenant import Tenant
    from .user import User
    from .group import Group
