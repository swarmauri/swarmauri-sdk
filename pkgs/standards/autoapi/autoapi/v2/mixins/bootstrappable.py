# bootstrappable.py
#from __future__ import annotations

import datetime as dt
from typing import Any, ClassVar, List

import sqlalchemy as sa
from sqlalchemy import event, insert
from sqlalchemy.orm import Mapped, mapped_column
# --------------------------------------------------------------------- #
# internal registry of every subclass that wants seeding
_BOOTSTRAPPABLES: list[type["Bootstrappable"]] = []
# --------------------------------------------------------------------- #


class Bootstrappable:
    """Inherit to auto-insert `DEFAULT_ROWS` right after schema creation."""
    DEFAULT_ROWS: ClassVar[List[dict[str, Any]]] = []

    # keep track of concrete subclasses that define defaults
    def __init_subclass__(cls, **kw):
        super().__init_subclass__(**kw)
        if cls.DEFAULT_ROWS:
            _BOOTSTRAPPABLES.append(cls)


# --------------------------------------------------------------------- #
# One single metadata-level hook – fires once per `create_all()` call.
# --------------------------------------------------------------------- #
@event.listens_for(Base.metadata, "after_create", once=True)
def _seed_all(target, connection, **kw):
    for cls in _BOOTSTRAPPABLES:
        # build dialect-specific insert --------------------------------
        dialect = connection.dialect.name
        if dialect in ("postgres", "postgresql"):
            from sqlalchemy.dialects.postgresql import insert as pg_insert

            stmt = pg_insert(cls).values(cls.DEFAULT_ROWS).on_conflict_do_nothing()
        else:                           # SQLite ≥ 3.35 or anything that accepts OR IGNORE
            stmt = sa.insert(cls).values(cls.DEFAULT_ROWS).prefix_with("OR IGNORE")
        # --------------------------------------------------------------
        connection.execute(stmt)
