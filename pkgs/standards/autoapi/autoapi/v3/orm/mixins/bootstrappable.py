from __future__ import annotations

from typing import Any, ClassVar, Iterable
import logging
import sqlalchemy as sa
from sqlalchemy import inspect as sa_inspect
from sqlalchemy.exc import IntegrityError

from ...types import Session, event

log = logging.getLogger(__name__)


class Bootstrappable:
    """
    Seed DEFAULT_ROWS for *this mapped class only* with zero magic.

    Rules:
      - Insert ONLY keys present on this class's mapped columns.
      - No auto defaults, no timestamp injection, no unique probing.
      - Idempotency only if ALL primary key columns are present in the row.
      - Listener is attached to cls.__table__ (no cross-class/global effects).
    """

    DEFAULT_ROWS: ClassVar[list[dict[str, Any]]] = []

    def __init_subclass__(cls, **kw):
        super().__init_subclass__(**kw)
        event.listen(
            cls.__table__, "after_create", cls._after_create_insert_default_rows
        )

    @classmethod
    def _after_create_insert_default_rows(cls, target, connection, **_):
        if not getattr(cls, "DEFAULT_ROWS", None):
            return
        from sqlalchemy.orm import sessionmaker

        SessionLocal = sessionmaker(bind=connection, future=True)
        db: Session = SessionLocal()
        try:
            cls._insert_rows(db, cls.DEFAULT_ROWS)
            db.commit()
        except Exception as e:
            db.rollback()
            log.warning(
                "Bootstrappable seed failed for %s: %s",
                cls.__name__,
                repr(e),
                exc_info=True,
            )
        finally:
            db.close()

    @classmethod
    def ensure_bootstrapped(
        cls, db: Session, rows: Iterable[dict[str, Any]] | None = None
    ) -> None:
        rows = cls.DEFAULT_ROWS if rows is None else list(rows)
        if rows:
            cls._insert_rows(db, rows)

    @classmethod
    def _insert_rows(cls, db: Session, rows: Iterable[dict[str, Any]]) -> None:
        mapper = sa_inspect(cls)

        # --- pick an insertable target (avoid boolean eval + avoid JOINs) ---
        local = mapper.local_table
        table = local if local is not None else mapper.persist_selectable
        if not hasattr(table, "insert"):  # e.g., persist_selectable is a JOIN
            table = mapper.local_table

        col_keys = {c.key for c in mapper.columns}
        pk_cols = list(table.primary_key.columns) if table.primary_key else []
        pk_keys = {c.key for c in pk_cols}

        def clean(r: dict[str, Any]) -> dict[str, Any]:
            # keep only columns mapped on THIS class
            return {k: r[k] for k in r.keys() & col_keys}

        payloads = [clean(r) for r in rows if r]
        if not payloads:
            return

        # Idempotent path if all PK columns are provided (per row)
        can_upsert = bool(pk_cols) and all(pk_keys <= set(p.keys()) for p in payloads)

        dialect = db.get_bind().dialect.name

        if can_upsert and dialect == "postgresql":
            from sqlalchemy.dialects.postgresql import insert as pg_insert

            stmt = (
                pg_insert(table)
                .values(payloads)
                .on_conflict_do_nothing(index_elements=[c.name for c in pk_cols])
            )
            db.execute(stmt)
            return

        if can_upsert and dialect == "sqlite":
            # Best-effort idempotency for SQLite
            from sqlalchemy.dialects.sqlite import insert as sqlite_insert

            db.execute(sqlite_insert(table).values(payloads).prefix_with("OR IGNORE"))
            return

        # Fallback: plain inserts; swallow duplicate races
        for p in payloads:
            try:
                db.execute(sa.insert(table).values(**p))
            except IntegrityError:
                db.rollback()  # treat as already present
