"""Persist versioned task records in SQLite."""

from .SqliteTaskStore import SqliteTaskStore

__version__ = "0.1.0"

__all__ = ["SqliteTaskStore"]
