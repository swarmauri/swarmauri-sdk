import sqlite3
from contextlib import closing
from pathlib import Path

from .RunState import RunState


class RunConflictError(RuntimeError):
    """Indicate another caller has already advanced the run."""


class SqliteRunStore:
    """Keep run checkpoints in an on-disk SQLite database."""

    def __init__(self, path: str | Path):
        self.path = Path(path)
        with closing(sqlite3.connect(self.path)) as conn, conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS runs "
                "(id TEXT PRIMARY KEY, revision INTEGER NOT NULL, "
                "state TEXT NOT NULL)"
            )

    def create(self, state: RunState) -> None:
        with closing(sqlite3.connect(self.path)) as conn, conn:
            conn.execute(
                "INSERT INTO runs VALUES (?, ?, ?)",
                (state.run_id, state.revision, state.model_dump_json()),
            )

    def load(self, run_id: str) -> RunState:
        with closing(sqlite3.connect(self.path)) as conn:
            row = conn.execute(
                "SELECT state FROM runs WHERE id = ?", (run_id,)
            ).fetchone()
        if row is None:
            raise KeyError(run_id)
        return RunState.model_validate_json(row[0])

    def save(self, state: RunState) -> RunState:
        updated = state.model_copy(update={"revision": state.revision + 1})
        with closing(sqlite3.connect(self.path)) as conn, conn:
            cursor = conn.execute(
                "UPDATE runs SET revision = ?, state = ? "
                "WHERE id = ? AND revision = ?",
                (
                    updated.revision,
                    updated.model_dump_json(),
                    state.run_id,
                    state.revision,
                ),
            )
            if cursor.rowcount != 1:
                raise RunConflictError(state.run_id)
        return updated
