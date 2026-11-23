"""Shared tasks contracts and immutable records."""

from .models import TaskRecord, TaskConflictError
from .ITaskStore import ITaskStore
from .ITaskManager import ITaskManager

__all__ = ["ITaskStore", "ITaskManager", "TaskRecord", "TaskConflictError"]
