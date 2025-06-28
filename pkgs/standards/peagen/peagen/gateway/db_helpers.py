# dqueue/db_helpers.py
import uuid
from swarmauri_standard.loggers.Logger import Logger
import datetime as dt
from typing import Any, Dict

from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession
import sqlalchemy as sa

from peagen.orm.status import Status
from peagen.orm import Base
from peagen.orm.config.secret import SecretModel
from peagen.orm.abuse_record import AbuseRecordModel
from peagen.orm.task.task_run import TaskRunModel
from peagen.orm.task.task_run_relation_association import (
    TaskRunTaskRelationAssociationModel,
)

log = Logger(name="upsert")


def _tenant_uuid(tid: str | uuid.UUID) -> uuid.UUID:
    """Return a ``uuid.UUID`` for *tid*.

    Accepts either a UUID instance, a valid UUID string, or an arbitrary
    slug-like string. Slug strings are mapped deterministically via
    :func:`uuid.uuid5` using the DNS namespace.
    """

    if isinstance(tid, uuid.UUID):
        return tid
    try:
        return uuid.UUID(str(tid))
    except ValueError:
        return uuid.uuid5(uuid.NAMESPACE_DNS, str(tid))


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


async def upsert_task(session: AsyncSession, row: TaskRunModel) -> None:
    data = _coerce(row.to_dict(exclude={"deps", "duration"}))
    stmt = (
        pg_insert(TaskRunModel)
        .values(**data)
        .on_conflict_do_update(
            index_elements=["id"],
            set_=_coerce(row.to_dict(exclude={"id", "deps", "duration"})),
        )
    )
    result = await session.execute(stmt)
    await session.execute(
        sa.delete(TaskRunTaskRelationAssociationModel).where(
            TaskRunTaskRelationAssociationModel.task_run_id == row.id
        )
    )
    values = [{"task_run_id": row.id, "relation_id": uuid.UUID(d)} for d in row.deps]
    if values:
        await session.execute(sa.insert(TaskRunTaskRelationAssociationModel), values)
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
    """Insert or update a secret for a tenant."""
    data = {
        "tenant_id": _tenant_uuid(tenant_id),
        "name": name,
        "cipher": cipher,
    }
    stmt = sa.insert(SecretModel).values(**data)
    if session.bind.dialect.name == "sqlite":
        stmt = stmt.prefix_with("OR REPLACE")
    else:
        stmt = stmt.on_conflict_do_update(
            index_elements=["tenant_id", "name"],
            set_={"cipher": cipher},
        )
    try:
        await session.execute(stmt)
    except sa.exc.OperationalError as exc:
        if "no such table" in str(exc).lower():
            await session.run_sync(
                lambda sync_sess: Base.metadata.create_all(bind=sync_sess.connection())
            )
            await session.execute(stmt)
        else:
            raise


async def fetch_secret(
    session: AsyncSession, tenant_id: str, name: str
) -> SecretModel | None:
    result = await session.execute(
        sa.select(SecretModel).where(
            SecretModel.tenant_id == _tenant_uuid(tenant_id), SecretModel.name == name
        )
    )
    return result.scalar_one_or_none()


async def delete_secret(session: AsyncSession, tenant_id: str, name: str) -> None:
    await session.execute(
        sa.delete(SecretModel).where(
            SecretModel.tenant_id == _tenant_uuid(tenant_id), SecretModel.name == name
        )
    )


async def record_unknown_handler(session: AsyncSession, ip: str) -> int:
    """Increment and return the unknown handler count for *ip*."""

    stmt = (
        pg_insert(AbuseRecordModel)
        .values(ip=ip, count=1, first_seen=dt.datetime.utcnow())
        .on_conflict_do_update(
            index_elements=["ip"],
            set_={"count": AbuseRecordModel.__table__.c.count + 1},
        )
        .returning(AbuseRecordModel.__table__.c.count)
    )
    result = await session.execute(stmt)
    (count,) = result.one()
    await session.commit()
    return count


async def fetch_banned_ips(session: AsyncSession) -> list[str]:
    """Return all IP addresses currently marked as banned."""

    result = await session.execute(
        sa.select(AbuseRecordModel.ip).where(AbuseRecordModel.banned.is_(True))
    )
    return [row[0] for row in result]


async def mark_ip_banned(session: AsyncSession, ip: str) -> None:
    """Set the banned flag for *ip*."""

    await session.execute(
        sa.update(AbuseRecordModel).where(AbuseRecordModel.ip == ip).values(banned=True)
    )
    await session.commit()
