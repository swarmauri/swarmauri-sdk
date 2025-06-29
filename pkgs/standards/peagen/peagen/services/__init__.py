from __future__ import annotations

from typing import Optional

import sqlalchemy as sa
from sqlalchemy.ext.asyncio import AsyncSession

from peagen.schemas import TaskCreate, TaskUpdate, TaskRead
from peagen.orm.task.task import TaskModel
from peagen.orm.task.task_run import TaskRunModel
from peagen.orm.status import Status


async def create_task(session: AsyncSession, task: TaskCreate) -> TaskRead:
    """Insert a new task row and return the created ``TaskRead``."""
    orm = TaskModel(**task.model_dump())
    session.add(orm)
    session.add(TaskRunModel(task_id=orm.id, status=Status.queued))
    await session.commit()
    await session.refresh(orm)
    return TaskRead.from_orm(orm)


async def get_task(session: AsyncSession, task_id: str) -> Optional[TaskRead]:
    """Return a ``TaskRead`` for *task_id* or ``None`` if missing."""
    row = await session.get(TaskModel, task_id)
    return TaskRead.from_orm(row) if row else None


async def update_task(session: AsyncSession, task_id: str, changes: TaskUpdate) -> None:
    """Apply ``changes`` to the existing task."""
    data = changes.model_dump(exclude_unset=True)
    if data:
        await session.execute(
            sa.update(TaskModel).where(TaskModel.id == task_id).values(**data)
        )
        await session.commit()


# helper used by RPC layer


def _to_schema(row: TaskModel) -> TaskRead:
    """Convert a ``TaskModel`` row to a ``TaskRead`` schema."""
    return TaskRead.from_orm(row)
