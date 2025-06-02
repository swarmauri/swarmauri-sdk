# dqueue/db_helpers.py
from sqlalchemy import insert
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession
from dqueue.models_sql import TaskRun

async def upsert_task(session: AsyncSession, row: TaskRun) -> None:
    stmt = (
        pg_insert(TaskRun)
        .values(**row.to_dict())                       # <-- helper method you add
        .on_conflict_do_update(
            index_elements=["id"],                     # primary key
            set_=row.to_dict(exclude={"id"}),          # update everything else
        )
    )
    await session.execute(stmt)