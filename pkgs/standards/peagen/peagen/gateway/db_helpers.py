# dqueue/db_helpers.py
import uuid
from swarmauri_standard.loggers.Logger import Logger
import datetime as dt
from typing import Dict, Any

from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy as sa
from peagen.models import Status, TaskRun, Manifest, TaskRevision

log = Logger(name="upsert")


def _coerce(row_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert  Enum → str,  UUID str → uuid.UUID,  dt.datetime → aware  dt.
    Ensures Postgres gets exactly the types it expects.
    """
    out = {}
    for k, v in row_dict.items():
        if v is None:
            out[k] = None
        elif isinstance(v, Status):
            out[k] = v.value  # 'running', 'success', …
        elif k == "id" and isinstance(v, str):
            out[k] = uuid.UUID(v)
        elif isinstance(v, dt.datetime) and v.tzinfo is None:
            out[k] = v.replace(tzinfo=dt.timezone.utc)
        else:
            out[k] = v
    return out


async def upsert_task(session: AsyncSession, row: TaskRun) -> None:
    data = _coerce(row.to_dict())
    stmt = (
        pg_insert(TaskRun)
        .values(**data)
        .on_conflict_do_update(
            index_elements=["id"],
            set_=_coerce(row.to_dict(exclude={"id"})),
        )
    )
    result = await session.execute(stmt)
    log.info("upsert rowcount=%s id=%s status=%s", result.rowcount, row.id, row.status)


async def upsert_manifest(session: AsyncSession, design_hash: str, plan_hash: str) -> Manifest:
    """Insert or retrieve a Manifest row by its hash pair."""
    stmt = (
        pg_insert(Manifest)
        .values(design_hash=design_hash, plan_hash=plan_hash)
        .on_conflict_do_nothing()
        .returning(Manifest)
    )
    result = await session.execute(stmt)
    row = result.fetchone()
    if row:
        return row[0]
    stmt = sa.select(Manifest).where(
        Manifest.design_hash == design_hash,
        Manifest.plan_hash == plan_hash,
    )
    row = (await session.execute(stmt)).scalar_one()
    return row


async def insert_revision(
    session: AsyncSession,
    task_id: str,
    rev_hash: str,
    payload_hash: str,
    payload_b64: str,
    parent_hash: str | None,
) -> None:
    """Insert a new TaskRevision row."""
    stmt = pg_insert(TaskRevision).values(
        task_id=task_id,
        rev_hash=rev_hash,
        parent_hash=parent_hash,
        payload_hash=payload_hash,
        payload_b64=payload_b64,
    )
    await session.execute(stmt)


async def latest_revision(session: AsyncSession, task_id: str) -> TaskRevision | None:
    stmt = (
        sa.select(TaskRevision)
        .where(TaskRevision.task_id == task_id)
        .order_by(TaskRevision.ts_created.desc())
        .limit(1)
    )
    result = await session.execute(stmt)
    return result.scalar_one_or_none()


async def ensure_status_enum(engine) -> None:
    """Ensure the Postgres ``status`` enum includes all ``Status`` values."""

    from sqlalchemy import text

    values = [s.value for s in Status]
    async with engine.begin() as conn:
        exists = await conn.execute(
            text("SELECT EXISTS(SELECT 1 FROM pg_type WHERE typname = 'status')")
        )
        if not exists.scalar():
            enum_values = ", ".join(f"'{v}'" for v in values)
            await conn.execute(
                text(f"CREATE TYPE IF NOT EXISTS status AS ENUM ({enum_values})")
            )
        else:
            res = await conn.execute(
                text(
                    "SELECT enumlabel FROM pg_enum JOIN pg_type ON pg_enum.enumtypid = pg_type.oid WHERE pg_type.typname = 'status'"
                )
            )
            present = {row[0] for row in res}
            for val in values:
                if val not in present:
                    await conn.execute(
                        text(f"ALTER TYPE status ADD VALUE IF NOT EXISTS '{val}'")
                    )
