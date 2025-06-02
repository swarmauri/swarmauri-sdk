# dqueue/db_helpers.py
from sqlalchemy.dialects.postgresql import insert as pg_insert
from .models_sql import TaskRun

async def upsert_task(session, row: TaskRun):
    stmt = (
        pg_insert(TaskRun)
        .values(row.to_dict())                       # full row
        .on_conflict_do_update(
            index_elements=["id"],
            set_=row.to_dict(exclude={"id"}),        # everything but PK
        )
    )
    await session.execute(stmt)
