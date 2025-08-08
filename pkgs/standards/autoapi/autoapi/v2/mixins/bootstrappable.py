from __future__ import annotations

from typing import Any, ClassVar, List

import logging
import sqlalchemy as sa
from sqlalchemy.exc import IntegrityError

log = logging.getLogger(__name__)


class Bootstrappable:
    """
    Seed DEFAULT_ROWS for *this mapped class only*, with zero automation.

    - Only inserts the literals you provide in DEFAULT_ROWS (no auto columns).
    - Per-class, per-table handler (attached to cls.__table__).
    - Executes once per table creation.
    - Postgres: INSERT ... ON CONFLICT DO NOTHING
      SQLite:   INSERT OR IGNORE
      Others:   plain INSERT; duplicate IntegrityError is swallowed.
    - Never re-raises from DDL hook (prevents KeyError('error') upstream).
    """

    DEFAULT_ROWS: ClassVar[List[dict[str, Any]]] = []

    def __init_subclass__(cls, **kw):
        super().__init_subclass__(**kw)

        # Attach to THIS class's table only; run only once when the table is created
        sa.event.listen(cls.__table__, "after_create", cls._seed_after_create, once=True)

    @classmethod
    def _seed_after_create(cls, target, connection, **kw):
        rows = getattr(cls, "DEFAULT_ROWS", None)
        if not rows:
            return

        table = cls.__table__
        dialect = connection.dialect.name

        try:
            if dialect in ("postgres", "postgresql"):
                from sqlalchemy.dialects.postgresql import insert as pg_insert

                stmt = pg_insert(table).values(rows).on_conflict_do_nothing()
                connection.execute(stmt)

            elif dialect == "sqlite":
                # Works on SQLite >= 3.24; OR IGNORE is widely supported
                stmt = sa.insert(table).values(rows).prefix_with("OR IGNORE")
                connection.execute(stmt)

            else:
                # Generic path: try plain insert, swallow duplicate races
                try:
                    connection.execute(sa.insert(table).values(rows))
                except IntegrityError:
                    # Some rows may already exist due to concurrent bootstrap; ignore
                    pass

        except Exception as e:
            # Do not bubble raw exceptions into your error normalizer
            log.warning(
                "Bootstrappable seed failed for %s on %s: %s",
                cls.__name__, dialect, repr(e),
                exc_info=True,
            )
            # continue startup

    # Optional runtime reseed (exact same semantics as above, zero magic)
    @classmethod
    def ensure_bootstrapped(cls, connection_or_session) -> None:
        """
        Manually seed DEFAULT_ROWS using an engine connection or ORM session.
        """
        rows = getattr(cls, "DEFAULT_ROWS", None)
        if not rows:
            return

        # Accept either Session or Connection
        if hasattr(connection_or_session, "connection"):
            # SQLAlchemy Session; get DB-API connection
            conn = connection_or_session.connection()
        else:
            # Already a Connection / AsyncConnection (sync only here)
            conn = connection_or_session

        cls._seed_after_create(cls.__table__, conn)  # reuse the same logic


__all__ = ["Bootstrappable"]
