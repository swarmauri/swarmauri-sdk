"""Persist revocable authority grants in SQLite."""

from .SqliteGrantStore import SqliteGrantStore

__version__ = "0.1.0"

__all__ = ["SqliteGrantStore"]
