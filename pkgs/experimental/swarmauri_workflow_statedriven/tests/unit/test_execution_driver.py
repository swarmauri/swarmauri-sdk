import pytest
from swarmauri_core.executions import ExecutionSnapshot
from swarmauri_workflow_statedriven import StateDrivenExecutionDriver
from swarmauri_workflow_statedriven.base import WorkflowBase
from swarmauri_workflow_statedriven.conditions.base import Condition
from swarmauri_workflow_statedriven.join_strategies.all_join import AllJoinStrategy

pytestmark = pytest.mark.unit


class Always(Condition):
    def evaluate(self, state):
        return True


class IdentityTool:
    def call(self, value):
        return value


async def test_join_buffers_survive_driver_reconstruction():
    def graph():
        workflow = WorkflowBase()
        for name in ("start", "left", "right"):
            workflow.add_state(name, tool=IdentityTool())
        workflow.add_state("join", tool=IdentityTool(), join_strategy=AllJoinStrategy())
        for source, target in (
            ("start", "left"),
            ("start", "right"),
            ("left", "join"),
            ("right", "join"),
        ):
            workflow.add_transition(source, target, Always())
        return workflow

    async def dispatch(name, data, snapshot):
        return name

    state = {"start": "start", "input": "brief"}
    steps = []
    for _ in range(10):
        driver = StateDrivenExecutionDriver(
            graph=graph(), definition_version="v1", dispatcher=dispatch
        )
        snapshot = ExecutionSnapshot("execution", "task", "graph", state=state)
        result = await driver.step(snapshot)
        steps.append(dict(result.state["results"]))
        state = result.state
        if result.completed:
            break
    assert list(steps[-1]) == ["start", "left", "right", "join"]
    assert "join" not in steps[2]
    assert not state["buffers"].get("join")
    changed = StateDrivenExecutionDriver(
        graph=graph(), definition_version="v2", dispatcher=dispatch
    )
    with pytest.raises(ValueError, match="version"):
        await changed.step(ExecutionSnapshot("execution", "task", "graph", state=state))
