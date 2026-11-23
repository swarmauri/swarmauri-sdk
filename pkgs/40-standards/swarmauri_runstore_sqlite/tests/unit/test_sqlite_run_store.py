from concurrent.futures import ThreadPoolExecutor
from threading import Barrier

from swarmauri_core.run_stores import (
    IRunStore,
    RunCheckpoint,
    RunConflictError,
)
from swarmauri_runstore_sqlite import SqliteRunStore


def test_only_one_process_can_save_an_expected_revision(tmp_path):
    db = tmp_path / "run.db"
    first = SqliteRunStore(path=db)
    second = SqliteRunStore(path=db)
    assert isinstance(first, IRunStore)
    first.create(RunCheckpoint("id", 0, "opaque text"))
    barrier = Barrier(2)

    def compete(store):
        checkpoint = store.load("id")
        barrier.wait(timeout=5)
        try:
            return store.save(checkpoint)
        except RunConflictError:
            return None

    with ThreadPoolExecutor(2) as pool:
        results = list(pool.map(compete, [first, second]))
    assert results.count(None) == 1
    assert first.load("id") == RunCheckpoint("id", 1, "opaque text")
