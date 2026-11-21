"""Coordinate business task lifecycle with existing execution controllers."""

import time
from dataclasses import replace
from typing import Literal
from uuid import uuid4

from pydantic import Field
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.tasks import TaskManagerBase
from swarmauri_core.tasks import ITaskStore, TaskRecord
from swarmauri_core.executions import IExecutionController


@ComponentBase.register_type(TaskManagerBase, "DefaultTaskManager")
class DefaultTaskManager(TaskManagerBase):
    """Persist task intent before coordinating attached executions.

    Task admission is a host operation after user authorization. Callers must
    not pass untrusted requested permissions as already admitted authority.
    """

    type: Literal["DefaultTaskManager"] = "DefaultTaskManager"
    store: ITaskStore = Field(exclude=True, repr=False)
    executions: IExecutionController = Field(exclude=True, repr=False)

    def start(self, subject, tenant, permissions, expires_at):
        if expires_at <= int(time.time()) or not permissions:
            raise ValueError("Admit non-empty, unexpired task authority")
        task = TaskRecord(
            str(uuid4()), subject, tenant, permissions, expires_at
        )
        self.store.create(task)
        return task

    def attach(self, task_id, execution_id):
        task = self.store.load(task_id)
        execution = self.executions.get(execution_id)
        if task.status != "active" or execution.task_id != task_id:
            raise ValueError("Execution cannot be attached to this task")
        return self.store.save(
            replace(
                task,
                execution_ids=tuple(
                    dict.fromkeys((*task.execution_ids, execution_id))
                ),
            )
        )

    def _transition(self, task_id, status, command):
        task = self.store.load(task_id)
        if task.status == "stopped" and status != "stopped":
            raise ValueError("A stopped task cannot be resumed")
        if status == "active" and task.expires_at <= int(time.time()):
            raise PermissionError("Task expired")
        if status == "active":
            for execution_id in task.execution_ids:
                if self.executions.get(execution_id).status in {
                    "running",
                    "pausing",
                    "stopping",
                }:
                    raise ValueError("Wait for executions to quiesce")
        # Persist intent first. Repeating pause/stop reconciles children
        # after an interrupted coordinator command.
        task = self.store.save(replace(task, status=status))
        for execution_id in task.execution_ids:
            execution = self.executions.get(execution_id)
            if execution.status not in {"completed", "failed", "stopped"}:
                getattr(self.executions, command)(execution_id)
        return task

    def pause(self, task_id):
        return self._transition(task_id, "paused", "pause")

    def resume(self, task_id):
        return self._transition(task_id, "active", "resume")

    def stop(self, task_id):
        return self._transition(task_id, "stopped", "stop")

    def assign(self, task_id, strategy, service_registry, roles=("agent",)):
        """Reuse ITaskMgmtStrategy for placement, not execution control."""
        task = self.store.load(task_id)
        strategy.assign_task(
            {"task_id": task.task_id},
            service_registry=lambda: service_registry.get_services_by_roles(
                list(roles)
            ),
        )
        return strategy.get_task(task.task_id)
