"""Adapt the existing model/tool runner to cooperative execution control."""

import asyncio
from typing import Any, Literal

from pydantic import Field
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.executions import ExecutionDriverBase
from swarmauri_core.executions import DriverStep, ExecutionCapabilities


@ComponentBase.register_type(ExecutionDriverBase, "AgentRunnerExecutionDriver")
class AgentRunnerExecutionDriver(ExecutionDriverBase):
    """Checkpoint between runner steps without changing its model protocol.

    Pause/stop do not interrupt a model/tool already running in a thread.
    Human interaction remains owned by AgentRunner.resume/decide.
    """

    type: Literal["AgentRunnerExecutionDriver"] = "AgentRunnerExecutionDriver"
    runner: Any = Field(exclude=True, repr=False)
    before_step: Any = Field(default=None, exclude=True, repr=False)

    def supports(self):
        return ExecutionCapabilities()

    async def step(self, snapshot):
        if self.before_step is not None:
            self.before_step(snapshot)
        state = dict(snapshot.state)
        run_id = state.get("run_id")
        if run_id is None:
            run_id = f"agent:{snapshot.execution_id}"
            # initialize() is deliberately separate from start().
            await asyncio.to_thread(
                self.runner.initialize, state["prompt"], run_id=run_id
            )
        current = await asyncio.to_thread(
            self.runner.advance, run_id, max_steps=1
        )
        return DriverStep(
            {**state, "run_id": run_id},
            completed=current.status == "completed",
            waiting=current.status in {"input_required", "approval_required"},
            result=current.result,
        )
