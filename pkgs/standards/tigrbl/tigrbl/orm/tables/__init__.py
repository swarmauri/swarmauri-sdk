"""Public façade for all table classes.

Usage
-----
    from tigrbl.orm.tables import (
        Tenant,
        User,
        Group,
        Role,
    )
"""

import importlib
from typing import TYPE_CHECKING, Any
from ._base import Base

__all__ = [
    "Tenant",
    "Client",
    "User",
    "Group",
    "Org",
    "Role",
    "RolePerm",
    "RoleGrant",
    "Status",
    "StatusEnum",
    "Change",
    "Base",
]

# ------------------------------------------------------------------ #
# Lazy attribute loader (PEP 562). Keeps import graphs light-weight.
# ------------------------------------------------------------------ #
_module_map = {
    "Tenant": f"{__name__}.tenant",
    "Client": f"{__name__}.client",
    "User": f"{__name__}.user",
    "Group": f"{__name__}.group",
    "Org": f"{__name__}.org",
    "Role": f"{__name__}.rbac",
    "RolePerm": f"{__name__}.rbac",
    "RoleGrant": f"{__name__}.rbac",
    "Status": f"{__name__}.status",
    "StatusEnum": f"{__name__}.status",
    "Change": f"{__name__}.audit",
}


def __getattr__(name: str) -> Any:  # noqa: D401
    """Dynamically import `tenant`, `user`, or `group` on first use."""
    if name not in _module_map:
        raise AttributeError(name)
    module = importlib.import_module(_module_map[name])
    obj = getattr(module, name)
    globals()[name] = obj  # cache for future look-ups
    return obj


# ------------------------------------------------------------------ #
# Static typing support – imported eagerly only during type checking.
# ------------------------------------------------------------------ #
if TYPE_CHECKING:  # pragma: no cover
    from ._base import Base
    from .tenant import Tenant
    from .client import Client
    from .user import User
    from .group import Group
    from .org import Org
    from .rbac import Role, RoleGrant, RolePerm
    from .status import Status, StatusEnum
    from .audit import Change
