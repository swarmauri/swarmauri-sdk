from __future__ import annotations

from peagen.orm.task.task_run import TaskRun
from .base import ResultBackendBase

Session = None
upsert_task = None


def _ensure_deps() -> None:
    global Session, upsert_task
    if Session is None or upsert_task is None:
        from peagen.gateway.db import Session as _Session
        from peagen.gateway.db_helpers import upsert_task as _upsert_task

        Session = _Session
        upsert_task = _upsert_task


class PostgresResultBackend(ResultBackendBase):
    """Store TaskRun rows in Postgres using the gateway's engine."""

    def __init__(self, dsn: str | None = None, **_: object) -> None:
        self.dsn = dsn  # unused but kept for future extension

    async def store(self, task_run: TaskRun) -> None:
        _ensure_deps()
        async with Session() as session:
            await upsert_task(session, task_run)
            await session.commit()
