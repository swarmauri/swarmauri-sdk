# autoapi/v2/mixins/bootstrappable.py
from typing import Any, ClassVar, List

from ..types import TableConfigProvider


class Bootstrappable(TableConfigProvider):
    """Inherit to auto-insert ``DEFAULT_ROWS`` right after table creation."""

    DEFAULT_ROWS: ClassVar[List[dict[str, Any]]] = []

    def __init_subclass__(cls, **kw):
        super().__init_subclass__(**kw)
        from autoapi.v2.types import event

        if cls.DEFAULT_ROWS:

            @event.listens_for(cls.__table__, "after_create", once=True)
            def _seed(target, connection, **kw):
                dialect = connection.dialect.name

                if dialect in ("postgres", "postgresql"):
                    from sqlalchemy.dialects.postgresql import insert as pg_insert

                    stmt = (
                        pg_insert(cls).values(cls.DEFAULT_ROWS).on_conflict_do_nothing()
                    )
                else:  # SQLite ≥ 3.35 or anything that accepts OR IGNORE
                    import sqlalchemy as sa

                    stmt = (
                        sa.insert(cls).values(cls.DEFAULT_ROWS).prefix_with("OR IGNORE")
                    )

                connection.execute(stmt)


__all__ = ["Bootstrappable"]


for _name in list(globals()):
    if _name not in __all__ and not _name.startswith("__"):
        del globals()[_name]


def __dir__():
    """Tighten ``dir()`` output for interactive sessions."""

    return sorted(__all__)
