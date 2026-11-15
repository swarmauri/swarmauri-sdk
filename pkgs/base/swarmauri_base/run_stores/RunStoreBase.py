from abc import abstractmethod
from dataclasses import replace
from typing import Literal

from swarmauri_core.run_stores import (
    IRunStore,
    RunCheckpoint,
    RunConflictError,
)

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes


@ComponentBase.register_model()
class RunStoreBase(IRunStore, ComponentBase):
    """Apply shared revision rules over atomic backend operations."""

    resource: Literal["RunStore"] = ResourceTypes.RUN_STORE.value
    type: Literal["RunStoreBase"] = "RunStoreBase"

    def create(self, checkpoint: RunCheckpoint) -> None:
        if checkpoint.revision != 0:
            raise ValueError("A new run must start at revision zero")
        if not self._insert(checkpoint):
            raise RunConflictError(checkpoint.run_id)

    def load(self, run_id: str) -> RunCheckpoint:
        checkpoint = self._read(run_id)
        if checkpoint is None:
            raise KeyError(run_id)
        return checkpoint

    def save(self, checkpoint: RunCheckpoint) -> RunCheckpoint:
        updated = replace(checkpoint, revision=checkpoint.revision + 1)
        if not self._compare_and_swap(checkpoint.revision, updated):
            raise RunConflictError(checkpoint.run_id)
        return updated

    @abstractmethod
    def _insert(self, checkpoint: RunCheckpoint) -> bool:
        pass

    @abstractmethod
    def _read(self, run_id: str) -> RunCheckpoint | None:
        pass

    @abstractmethod
    def _compare_and_swap(
        self, expected: int, checkpoint: RunCheckpoint
    ) -> bool:
        pass
