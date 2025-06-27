"""Database operations for ``Task`` objects."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from peagen.orm.task.task import TaskModel
from peagen.schemas import TaskCreate, TaskRead, TaskUpdate


def _to_orm(data: TaskCreate | TaskUpdate) -> TaskModel:
    return TaskModel(**data.model_dump())


def _to_schema(row: TaskModel) -> TaskRead:
    return TaskRead.from_orm(row)


async def create_task(db: AsyncSession, data: TaskCreate) -> TaskRead:
    """Persist a new ``Task`` and return the created row."""

    obj = _to_orm(data)
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return _to_schema(obj)


async def get_task(db: AsyncSession, task_id: str) -> TaskRead | None:
    """Return a task by its ID."""

    result = await db.execute(select(TaskModel).where(TaskModel.id == task_id))
    row = result.scalar_one_or_none()
    return _to_schema(row) if row else None


async def update_task(
    db: AsyncSession, task_id: str, data: TaskUpdate
) -> TaskRead | None:
    """Update a task with ``data`` and return the updated row."""

    result = await db.execute(select(TaskModel).where(TaskModel.id == task_id))
    obj = result.scalar_one_or_none()
    if obj is None:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(obj, field, value)
    await db.commit()
    await db.refresh(obj)
    return _to_schema(obj)
