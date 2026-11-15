import sqlite3
from contextlib import closing
from pathlib import Path
from typing import Literal

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.run_stores import RunStoreBase
from swarmauri_core.run_stores import RunCheckpoint


@ComponentBase.register_type(RunStoreBase, "SqliteRunStore")
class SqliteRunStore(RunStoreBase):
    """Persist opaque run checkpoints in an on-disk SQLite database."""

    path: Path
    type: Literal["SqliteRunStore"] = "SqliteRunStore"

    def model_post_init(self, context):
        with closing(sqlite3.connect(self.path)) as conn, conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS runs "
                "(id TEXT PRIMARY KEY, revision INTEGER NOT NULL, "
                "state TEXT NOT NULL)"
            )

    def _insert(self, checkpoint: RunCheckpoint) -> bool:
        with closing(sqlite3.connect(self.path)) as conn, conn:
            cursor = conn.execute(
                "INSERT INTO runs (id, revision, state) VALUES (?, ?, ?) "
                "ON CONFLICT(id) DO NOTHING",
                (checkpoint.run_id, checkpoint.revision, checkpoint.payload),
            )
            return cursor.rowcount == 1

    def _read(self, run_id: str) -> RunCheckpoint | None:
        with closing(sqlite3.connect(self.path)) as conn:
            row = conn.execute(
                "SELECT revision, state FROM runs WHERE id = ?", (run_id,)
            ).fetchone()
        return None if row is None else RunCheckpoint(run_id, *row)

    def _compare_and_swap(
        self, expected: int, checkpoint: RunCheckpoint
    ) -> bool:
        with closing(sqlite3.connect(self.path)) as conn, conn:
            cursor = conn.execute(
                "UPDATE runs SET revision = ?, state = ? "
                "WHERE id = ? AND revision = ?",
                (
                    checkpoint.revision,
                    checkpoint.payload,
                    checkpoint.run_id,
                    expected,
                ),
            )
            return cursor.rowcount == 1
