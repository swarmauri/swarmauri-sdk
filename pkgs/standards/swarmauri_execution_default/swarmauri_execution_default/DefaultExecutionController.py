"""Cooperative execution control using the existing checkpoint contract."""

import asyncio
import json
import time
from dataclasses import asdict, replace
from typing import Literal
from uuid import uuid4

from pydantic import Field
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.executions import ExecutionControllerBase
from swarmauri_core.executions import (
    ExecutionSnapshot,
    IExecutionDriver,
)
from swarmauri_core.run_stores import IRunStore, RunCheckpoint
from swarmauri_core.tasks import ITaskStore


@ComponentBase.register_type(
    ExecutionControllerBase, "DefaultExecutionController"
)
class DefaultExecutionController(ExecutionControllerBase):
    """Fence concurrent dispatch and checkpoint cooperative boundaries.

    A running checkpoint is never replayed automatically after a crash.
    Hosts reconcile uncertain side effects before replacing that execution.
    """

    type: Literal["DefaultExecutionController"] = "DefaultExecutionController"
    checkpoints: IRunStore = Field(exclude=True, repr=False)
    tasks: ITaskStore = Field(exclude=True, repr=False)
    drivers: dict[str, IExecutionDriver] = Field(exclude=True, repr=False)

    def _save(self, snapshot):
        checkpoint = self.checkpoints.save(
            RunCheckpoint(
                snapshot.execution_id,
                snapshot.revision,
                json.dumps({"format": "execution.v1", **asdict(snapshot)}),
            )
        )
        return replace(snapshot, revision=checkpoint.revision)

    def get(self, execution_id):
        checkpoint = self.checkpoints.load(execution_id)
        data = json.loads(checkpoint.payload)
        if data.pop("format", None) != "execution.v1":
            raise ValueError("Unknown execution checkpoint version")
        if data["execution_id"] != execution_id:
            raise ValueError("Execution checkpoint identity mismatch")
        data["revision"] = checkpoint.revision
        return ExecutionSnapshot(**data)

    def start(self, task_id, driver, state=None, parent_id=None):
        task = self.tasks.load(task_id)
        if task.status != "active" or task.expires_at <= int(time.time()):
            raise PermissionError("Task is inactive or expired")
        if driver not in self.drivers:
            raise KeyError(driver)
        if parent_id:
            parent = self.get(parent_id)
            if parent.task_id != task_id or parent.status not in {
                "ready",
                "running",
            }:
                raise ValueError("Parent cannot admit child work")
        snapshot = ExecutionSnapshot(
            str(uuid4()),
            task_id,
            driver,
            state=dict(state or {}),
            parent_id=parent_id,
        )
        self.checkpoints.create(
            RunCheckpoint(
                snapshot.execution_id,
                0,
                json.dumps({"format": "execution.v1", **asdict(snapshot)}),
            )
        )
        # Attach every child to the task's durable cancellation group.
        self.tasks.save(
            replace(
                task,
                execution_ids=(*task.execution_ids, snapshot.execution_id),
            )
        )
        return snapshot

    async def advance(self, execution_id):
        snapshot = self.get(execution_id)
        if snapshot.status != "ready":
            return snapshot
        task = self.tasks.load(snapshot.task_id)
        if execution_id not in task.execution_ids:
            raise PermissionError("Execution is not attached to its task")
        if task.status == "paused":
            return self.pause(execution_id)
        if task.status != "active" or task.expires_at <= int(time.time()):
            return self.stop(execution_id)
        # CAS makes one worker the dispatch owner.
        running = self._save(replace(snapshot, status="running"))
        try:
            step = await self.drivers[running.driver].step(running)
        except asyncio.CancelledError:
            current = self.get(execution_id)
            self._save(
                replace(current, status="failed", error="Dispatch interrupted")
            )
            raise
        except Exception as exc:
            current = self.get(execution_id)
            return self._save(
                replace(current, status="failed", error=type(exc).__name__)
            )
        current = self.get(execution_id)
        task = self.tasks.load(current.task_id)
        if (
            current.status == "stopping"
            or task.status == "stopped"
            or task.expires_at <= int(time.time())
        ):
            status = "stopped"
        elif step.completed:
            status = "completed"
        elif current.status == "pausing" or task.status == "paused":
            status = "paused"
        elif step.waiting:
            status = "waiting"
        else:
            status = "ready"
        return self._save(
            replace(
                current, status=status, state=step.state, result=step.result
            )
        )

    def _command(self, execution_id, command):
        current = self.get(execution_id)
        if current.status in {"stopped", "completed", "failed"}:
            return current
        capabilities = self.drivers[current.driver].supports()
        if not getattr(capabilities, command):
            raise NotImplementedError(command)
        if command == "pause":
            if current.status == "stopping":
                return current
            status = (
                "pausing"
                if current.status in {"running", "pausing"}
                else "paused"
            )
        elif command == "stop":
            status = (
                "stopping"
                if current.status in {"running", "pausing", "stopping"}
                else "stopped"
            )
        else:
            task = self.tasks.load(current.task_id)
            if task.status != "active" or task.expires_at <= int(time.time()):
                raise PermissionError("Task cannot resume")
            if current.status not in {"paused", "waiting", "ready"}:
                raise ValueError("Wait for the execution to quiesce")
            status = "ready"
        return self._save(replace(current, status=status))

    def pause(self, execution_id):
        return self._command(execution_id, "pause")

    def resume(self, execution_id):
        return self._command(execution_id, "resume")

    def stop(self, execution_id):
        current = self._command(execution_id, "stop")
        task = self.tasks.load(current.task_id)
        for child_id in task.execution_ids:
            if self.get(child_id).parent_id == execution_id:
                self.stop(child_id)
        return current
