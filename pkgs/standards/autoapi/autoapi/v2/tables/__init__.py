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
}

def __getattr__(name: str) -> ModuleType:          # PEP-562 lazy import hook
    if name in _table_map:
        mod = importlib.import_module(_table_map[name])
        setattr(sys.modules[__name__], name, mod)  # cache
        return mod
    raise AttributeError(name)


metadata = sa.MetaData(schema=None)           # shared across package & user
class Base(DeclarativeBase):
    metadata = metadata
