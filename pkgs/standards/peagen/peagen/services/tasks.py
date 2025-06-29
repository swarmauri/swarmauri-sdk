"""Compatibility helpers for task schema conversions."""

from peagen.schemas import TaskRead
from peagen.orm.task.task import TaskModel


def _to_schema(row: TaskModel) -> TaskRead:
    """Convert a ``TaskModel`` row to a ``TaskRead`` schema."""
    return TaskRead.from_orm(row)
