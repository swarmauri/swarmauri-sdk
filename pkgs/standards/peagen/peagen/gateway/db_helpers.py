# dqueue/db_helpers.py
import uuid
from swarmauri_standard.loggers.Logger import Logger
import datetime as dt
from typing import Dict, Any

from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy as sa
from peagen.models import Status, TaskRun, TaskRunDep
from peagen.models.secret import Secret

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
    data = _coerce(row.to_dict(exclude={"deps"}))
    stmt = (
        pg_insert(TaskRun)
        .values(**data)
        .on_conflict_do_update(
            index_elements=["id", "tenant_id"],
            set_=_coerce(row.to_dict(exclude={"id", "tenant_id", "deps"})),
        )
    )
    result = await session.execute(stmt)
    await session.execute(sa.delete(TaskRunDep).where(TaskRunDep.task_id == row.id))
    values = [{"task_id": row.id, "dep_id": uuid.UUID(d)} for d in row.deps]
    if values:
        await session.execute(sa.insert(TaskRunDep), values)
    log.info("upsert rowcount=%s id=%s status=%s", result.rowcount, row.id, row.status)


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
            await conn.execute(text(f"CREATE TYPE status AS ENUM ({enum_values})"))
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


async def upsert_secret(
    session: AsyncSession,
    tenant_id: str,
    owner_fpr: str,
    name: str,
    cipher: str,
) -> None:
    data = {
        "tenant_id": tenant_id,
        "owner_fpr": owner_fpr,
        "name": name,
        "cipher": cipher,
        "created_at": dt.datetime.utcnow(),
    }
    stmt = (
        pg_insert(Secret)
        .values(**data)
        .on_conflict_do_update(
            index_elements=["tenant_id", "name"],
            set_={
                "cipher": cipher,
                "owner_fpr": owner_fpr,
                "created_at": data["created_at"],
            },
        )
    )
    await session.execute(stmt)


async def fetch_secret(
    session: AsyncSession, tenant_id: str, name: str
) -> Secret | None:
    result = await session.execute(
        sa.select(Secret).where(Secret.tenant_id == tenant_id, Secret.name == name)
    )
    return result.scalar_one_or_none()


async def delete_secret(session: AsyncSession, tenant_id: str, name: str) -> None:
    await session.execute(
        sa.delete(Secret).where(Secret.tenant_id == tenant_id, Secret.name == name)
    )
