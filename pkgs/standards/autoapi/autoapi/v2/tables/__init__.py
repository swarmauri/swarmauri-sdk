# autoapi/tables/__init__.py
import importlib, sys
from types import ModuleType

import sqlalchemy as sa
from sqlalchemy.orm import DeclarativeBase


# map short names → real sub-modules
_table_map = {
    "audit":   "autoapi.v2.tables.audit",
    "rbac":    "autoapi.v2.tables.rbac",
    "tenancy": "autoapi.v2.tables.tenancy",
    "Tenant": "autoapi.v2.tables.tenancy.tenant",
    "User":   "autoapi.v2.tables.tenancy.user",
    "Group":  "autoapi.v2.tables.tenancy.group",
}

def __getattr__(name: str) -> ModuleType:          # PEP-562 lazy import hook
    if name in _table_map:
        mod = importlib.import_module(_table_map[name])
        setattr(sys.modules[__name__], name, mod)  # cache
        return mod
    raise AttributeError(name)

class Base(DeclarativeBase):
    metadata = sa.MetaData(schema=None) 
