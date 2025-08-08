from __future__ import annotations

from typing import Any, ClassVar, Iterable, List, Sequence
from datetime import datetime, timezone

import sqlalchemy as sa
from sqlalchemy.orm import Session, inspect as sa_inspect
from sqlalchemy.exc import IntegrityError

from ..types import TableConfigProvider


class Bootstrappable(TableConfigProvider):
    """
    Inherit to auto-insert `DEFAULT_ROWS` after table creation *for this class only*.

    - Uses only columns declared on the mapped class (and its parents via inheritance).
    - Skips unknown columns (so minimal Peagen tenants don't have to satisfy AuthN fields).
    - Auto-fills `created_at` / `updated_at` if those columns exist and aren’t provided.
    - Idempotent: uses ON CONFLICT DO NOTHING on Postgres; falls back to get-or-create elsewhere.
    """

    DEFAULT_ROWS: ClassVar[List[dict[str, Any]]] = []

    # If you also want runtime/manual bootstrapping (not only after_create), call:
    #   MyModel.ensure_bootstrapped(db)
    # or pass a custom rows iterable: MyModel.ensure_bootstrapped(db, rows=[...])

    def __init_subclass__(cls, **kw):
        super().__init_subclass__(**kw)
        # Register a SQLAlchemy event on THIS class's table only
        if getattr(cls, "DEFAULT_ROWS", None):
            sa.event.listen(
                cls.__table__, "after_create", cls._after_create_insert_default_rows
            )

    # ──────────────────────────────────────────────────────────────────────
    # SQLA event entrypoint
    # ──────────────────────────────────────────────────────────────────────
    @classmethod
    def _after_create_insert_default_rows(cls, target, connection, **_):
        # Run within a short-lived session bound to the DDL connection
        from sqlalchemy.orm import sessionmaker

        SessionLocal = sessionmaker(bind=connection)
        db = SessionLocal()
        try:
            cls._insert_rows(db, cls.DEFAULT_ROWS)
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    # ──────────────────────────────────────────────────────────────────────
    # Public API
    # ──────────────────────────────────────────────────────────────────────
    @classmethod
    def ensure_bootstrapped(
        cls, db: Session, rows: Iterable[dict[str, Any]] | None = None
    ) -> None:
        if rows is None:
            rows = cls.DEFAULT_ROWS
        if not rows:
            return
        cls._insert_rows(db, rows)

    # ──────────────────────────────────────────────────────────────────────
    # Core impl
    # ──────────────────────────────────────────────────────────────────────
    @classmethod
    def _insert_rows(cls, db: Session, rows: Iterable[dict[str, Any]]) -> None:
        mapper = sa_inspect(cls)
        table = mapper.local_table or mapper.persist_selectable  # mapped Table
        col_map = {c.key: c for c in mapper.columns}  # ORM key -> Column
        now = datetime.now(timezone.utc)

        # Detect conflict target: prefer PK; else first unique constraint/index; else None
        pk_cols: Sequence[sa.Column] = (
            list(table.primary_key.columns) if table.primary_key else []
        )
        unique_sets: list[list[sa.Column]] = []
        for c in table.columns:
            if c.unique:
                unique_sets.append([c])
        for uc in getattr(table, "constraints", set()):
            if isinstance(uc, sa.UniqueConstraint):
                unique_sets.append(list(uc.columns))
        conflict_cols = pk_cols or (unique_sets[0] if unique_sets else [])

        # Build clean payloads per row using only declared columns
        def to_payload(r: dict[str, Any]) -> dict[str, Any]:
            p = {}
            for k, v in r.items():
                if k in col_map:
                    p[k] = v() if callable(v) else v
            # timestamp conveniences if present
            if "created_at" in col_map and "created_at" not in p:
                p["created_at"] = now
            if "updated_at" in col_map and "updated_at" not in p:
                p["updated_at"] = now
            return p

        payloads = [to_payload(r) for r in rows if r]

        if not payloads:
            return

        # Try a bulk UPSERT for Postgres; otherwise graceful fallback
        try:
            from sqlalchemy.dialects.postgresql import insert as pg_insert  # type: ignore

            stmt = pg_insert(table).values(payloads)
            if conflict_cols:
                stmt = stmt.on_conflict_do_nothing(
                    index_elements=[c.name for c in conflict_cols]
                )
            else:
                stmt = stmt.on_conflict_do_nothing()

            db.execute(stmt)
        except Exception:
            # Fallback: per-row "get or create" to remain cross-dialect
            for p in payloads:
                if not p:
                    continue
                if conflict_cols:
                    filters = {c.key: p.get(c.key) for c in conflict_cols if c.key in p}
                    if filters and db.query(cls).filter_by(**filters).first():
                        continue
                # Last-resort insert; swallow race duplicates
                try:
                    obj = cls(**p)
                    db.add(obj)
                    db.flush()
                except IntegrityError:
                    db.rollback()  # another worker inserted it first
                    continue


__all__ = ["Bootstrappable"]
