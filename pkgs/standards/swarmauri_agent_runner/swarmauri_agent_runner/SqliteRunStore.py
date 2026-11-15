"""Compatibility API for the original typed SQLite store."""

from pathlib import Path

from swarmauri_core.run_stores import RunConflictError

from ._checkpoint_codec import encode_checkpoint
from .RunState import RunState

__all__ = ["RunConflictError", "SqliteRunStore"]


class SqliteRunStore:
    """Use swarmauri_runstore_sqlite for new integrations."""

    def __init__(self, path: str | Path):
        from swarmauri_runstore_sqlite import SqliteRunStore as CheckpointStore

        self._store = CheckpointStore(path=path)
        self.path = self._store.path

    def create(self, state: RunState) -> None:
        self._store.create(encode_checkpoint(state))

    def load(self, run_id: str) -> RunState:
        return RunState.from_checkpoint(self._store.load(run_id))

    def save(self, state: RunState) -> RunState:
        return RunState.from_checkpoint(
            self._store.save(encode_checkpoint(state, advance=True))
        )
