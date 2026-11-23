"""SQLite grants repository with optimistic concurrency."""

from pathlib import Path
from typing import Literal

from pydantic import PrivateAttr
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.delegation import GrantStoreBase
from swarmauri_base._sqlite_records import SqliteRecords
from swarmauri_core.delegation import Grant, GrantConflictError


@ComponentBase.register_type(GrantStoreBase, "SqliteGrantStore")
class SqliteGrantStore(GrantStoreBase):
    """Persist grants in independent, atomic SQLite transactions."""

    type: Literal["SqliteGrantStore"] = "SqliteGrantStore"
    path: Path
    _records: SqliteRecords = PrivateAttr()

    def model_post_init(self, context):
        self._records = SqliteRecords(
            self.path, "grants", Grant, GrantConflictError
        )

    def create(self, record):
        self._records.create(record)

    def load(self, identifier):
        return self._records.load(identifier)

    def save(self, record):
        return self._records.save(record)
