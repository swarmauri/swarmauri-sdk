# dqueue/db_helpers.py
import uuid
from swarmauri_standard.loggers.Logger import Logger
import datetime as dt
from typing import Dict, Any

from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession
from peagen.models import Status, TaskRun

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
            out[k] = v.value           # 'running', 'success', …
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


