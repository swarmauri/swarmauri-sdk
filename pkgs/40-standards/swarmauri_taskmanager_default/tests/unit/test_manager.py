import time
import pytest
from swarmauri_execution_default import DefaultExecutionController
from swarmauri_taskmanager_default import DefaultTaskManager
from swarmauri_taskstore_sqlite import SqliteTaskStore
from swarmauri_runstore_sqlite import SqliteRunStore
from swarmauri_core.permissions import Permission
from swarmauri_standard.task_mgmt_strategies.RoundRobinStrategy import (
    RoundRobinStrategy,
)
from swarmauri_standard.service_registries.ServiceRegistry import (
    ServiceRegistry,
)

pytestmark = pytest.mark.unit


def test_assignment_reuses_existing_registry_and_strategy(tmp_path):
    store = SqliteTaskStore(path=tmp_path / "tasks.db")
    controller = DefaultExecutionController(
        tasks=store,
        checkpoints=SqliteRunStore(path=tmp_path / "runs.db"),
        drivers={},
    )
    manager = DefaultTaskManager(store=store, executions=controller)
    task = manager.start(
        "alice",
        "tenant",
        (Permission("read", "doc", "tenant"),),
        int(time.time()) + 60,
    )
    services = ServiceRegistry()
    services.register_service("research", {"role": "agent"})
    strategy = RoundRobinStrategy()
    assert manager.assign(task.task_id, strategy, services) == {
        "task_id": task.task_id,
        "assigned_service": "research",
    }
    assert manager.pause(task.task_id).status == "paused"
    assert manager.resume(task.task_id).status == "active"
    assert manager.stop(task.task_id).status == "stopped"
    assert manager.stop(task.task_id).status == "stopped"
    with pytest.raises(ValueError):
        manager.resume(task.task_id)
