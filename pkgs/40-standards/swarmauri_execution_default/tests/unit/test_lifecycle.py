import asyncio
import time
from dataclasses import replace
from typing import Any, Literal
import pytest
from pydantic import Field
from swarmauri_base.executions import ExecutionDriverBase
from swarmauri_core.executions import DriverStep, ExecutionCapabilities
from swarmauri_core.permissions import Permission
from swarmauri_core.tasks import TaskRecord
from swarmauri_taskstore_sqlite import SqliteTaskStore
from swarmauri_runstore_sqlite import SqliteRunStore
from swarmauri_execution_default import DefaultExecutionController

pytestmark = pytest.mark.unit


class CounterDriver(ExecutionDriverBase):
    type: Literal["CounterDriver"] = "CounterDriver"
    entered: Any = Field(default=None, exclude=True)
    release: Any = Field(default=None, exclude=True)

    def supports(self):
        return ExecutionCapabilities()

    async def step(self, snapshot):
        if self.entered:
            self.entered.set()
            await self.release.wait()
        count = snapshot.state.get("count", 0) + 1
        return DriverStep({"count": count}, completed=count == 3, result=count)


def runtime(tmp_path, driver=None):
    tasks = SqliteTaskStore(path=tmp_path / "tasks.db")
    tasks.create(
        TaskRecord(
            "task",
            "alice",
            "tenant",
            (Permission("read", "doc", "tenant"),),
            int(time.time()) + 60,
        )
    )
    controller = DefaultExecutionController(
        checkpoints=SqliteRunStore(path=tmp_path / "runs.db"),
        tasks=tasks,
        drivers={"counter": driver or CounterDriver()},
    )
    return tasks, controller


async def test_pause_restart_resume_and_no_dispatch_after_stop(tmp_path):
    tasks, first = runtime(tmp_path)
    execution = first.start("task", "counter")
    execution = await first.advance(execution.execution_id)
    assert execution.state["count"] == 1
    first.pause(execution.execution_id)
    restarted = DefaultExecutionController(
        checkpoints=SqliteRunStore(path=tmp_path / "runs.db"),
        tasks=tasks,
        drivers={"counter": CounterDriver()},
    )
    assert (await restarted.advance(execution.execution_id)).status == "paused"
    restarted.resume(execution.execution_id)
    assert (await restarted.advance(execution.execution_id)).state[
        "count"
    ] == 2
    restarted.stop(execution.execution_id)
    assert (await restarted.advance(execution.execution_id)).state[
        "count"
    ] == 2
    assert restarted.get(execution.execution_id).status == "stopped"


async def test_pause_acknowledges_inflight_boundary_and_fences_worker(
    tmp_path,
):
    entered, release = asyncio.Event(), asyncio.Event()
    tasks, controller = runtime(
        tmp_path, CounterDriver(entered=entered, release=release)
    )
    execution = controller.start("task", "counter")
    pending = asyncio.create_task(controller.advance(execution.execution_id))
    await entered.wait()
    assert (
        await controller.advance(execution.execution_id)
    ).status == "running"
    assert controller.pause(execution.execution_id).status == "pausing"
    with pytest.raises(ValueError):
        controller.resume(execution.execution_id)
    release.set()
    assert (await pending).status == "paused"
    assert controller.get(execution.execution_id).state["count"] == 1


async def test_task_status_blocks_attached_children(tmp_path):
    tasks, controller = runtime(tmp_path)
    parent = controller.start("task", "counter")
    child = controller.start("task", "counter", parent_id=parent.execution_id)
    task = tasks.load("task")
    assert set(task.execution_ids) == {parent.execution_id, child.execution_id}
    tasks.save(replace(task, status="stopped"))
    assert (await controller.advance(child.execution_id)).status == "stopped"


async def test_stop_wins_over_pause_and_reaches_descendants(tmp_path):
    entered, release = asyncio.Event(), asyncio.Event()
    tasks, controller = runtime(
        tmp_path, CounterDriver(entered=entered, release=release)
    )
    parent = controller.start("task", "counter")
    child = controller.start("task", "counter", parent_id=parent.execution_id)
    pending = asyncio.create_task(controller.advance(parent.execution_id))
    await entered.wait()
    assert controller.stop(parent.execution_id).status == "stopping"
    assert controller.pause(parent.execution_id).status == "stopping"
    assert controller.get(child.execution_id).status == "stopped"
    with pytest.raises(ValueError):
        controller.start("task", "counter", parent_id=parent.execution_id)
    release.set()
    assert (await pending).status == "stopped"
