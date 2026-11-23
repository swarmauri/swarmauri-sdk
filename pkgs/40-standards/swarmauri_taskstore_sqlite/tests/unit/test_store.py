import time
from dataclasses import replace
import pytest
from swarmauri_core.permissions import Permission
from swarmauri_core.tasks import TaskRecord, TaskConflictError
from swarmauri_taskstore_sqlite import SqliteTaskStore

pytestmark = pytest.mark.unit


def test_restart_and_atomic_revision_conflicts(tmp_path):
    path = tmp_path / "tasks.db"
    first = SqliteTaskStore(path=path)
    task = TaskRecord(
        "task",
        "alice",
        "tenant",
        (Permission("read", "doc", "tenant"),),
        int(time.time()) + 60,
    )
    first.create(task)
    second = SqliteTaskStore(path=path)
    assert second.load("task") == task
    changed = second.save(replace(task, status="paused"))
    assert changed.revision == 1
    with pytest.raises(TaskConflictError):
        first.save(replace(task, status="stopped"))
    with pytest.raises(TaskConflictError):
        first.create(task)
    assert first.load("task").status == "paused"
    with pytest.raises(KeyError):
        first.load("unknown")
