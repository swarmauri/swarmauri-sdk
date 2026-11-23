"""SQLite tasks repository with optimistic concurrency."""

from pathlib import Path
from typing import Literal

from pydantic import PrivateAttr
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.tasks import TaskStoreBase
from swarmauri_base._sqlite_records import SqliteRecords
from swarmauri_core.tasks import TaskRecord, TaskConflictError


@ComponentBase.register_type(TaskStoreBase, "SqliteTaskStore")
class SqliteTaskStore(TaskStoreBase):
    """Persist tasks in independent, atomic SQLite transactions."""

    type: Literal["SqliteTaskStore"] = "SqliteTaskStore"
    path: Path
    _records: SqliteRecords = PrivateAttr()

    def model_post_init(self, context):
        self._records = SqliteRecords(
            self.path, "tasks", TaskRecord, TaskConflictError
        )

    def create(self, record):
        self._records.create(record)

    def load(self, identifier):
        return self._records.load(identifier)

    def save(self, record):
        return self._records.save(record)
