import pytest
from pydantic import PrivateAttr
from swarmauri_core.run_stores import RunCheckpoint, RunConflictError

from swarmauri_base.run_stores import RunStoreBase


class ExampleStore(RunStoreBase):
    _checkpoints: dict = PrivateAttr(default_factory=dict)

    def _insert(self, checkpoint):
        if checkpoint.run_id in self._checkpoints:
            return False
        self._checkpoints[checkpoint.run_id] = checkpoint
        return True

    def _read(self, run_id):
        return self._checkpoints.get(run_id)

    def _compare_and_swap(self, expected, checkpoint):
        existing = self._read(checkpoint.run_id)
        if existing is None or existing.revision != expected:
            return False
        self._checkpoints[checkpoint.run_id] = checkpoint
        return True


def test_shared_revision_behavior():
    store = ExampleStore()
    assert store.resource == "RunStore"
    with pytest.raises(KeyError):
        store.load("run")
    with pytest.raises(ValueError, match="revision zero"):
        store.create(RunCheckpoint("run", 1, "data"))
    initial = RunCheckpoint("run", 0, "data")
    store.create(initial)
    with pytest.raises(RunConflictError):
        store.create(initial)
    saved = store.save(initial)
    assert saved == store.load("run")
    assert saved.revision == 1
    assert initial.revision == 0
    with pytest.raises(RunConflictError):
        store.save(initial)
