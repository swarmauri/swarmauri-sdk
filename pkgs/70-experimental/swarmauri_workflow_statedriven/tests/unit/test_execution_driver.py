import pytest
import json
from swarmauri_core.executions import ExecutionSnapshot
from swarmauri_workflow_statedriven import StateDrivenExecutionDriver
from swarmauri_workflow_statedriven.base import WorkflowBase
from swarmauri_workflow_statedriven.conditions.base import Condition
from swarmauri_workflow_statedriven.join_strategies.all_join import (
    AllJoinStrategy,
)

pytestmark = [pytest.mark.unit, pytest.mark.asyncio]


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
        workflow.add_state(
            "join", tool=IdentityTool(), join_strategy=AllJoinStrategy()
        )
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
        await changed.step(
            ExecutionSnapshot("execution", "task", "graph", state=state)
        )


@pytest.mark.parametrize("remote_dispatch", [False, True])
async def test_split_expansion_survives_checkpoint_and_driver_restart(
    remote_dispatch,
):
    from swarmauri_workflow_statedriven.input_modes.split import SplitInputMode

    dispatched = []

    class RecordingTool:
        def call(self, value):
            dispatched.append(value)
            return value

    def graph():
        workflow = WorkflowBase()
        workflow.add_state(
            "split", tool=RecordingTool(), input_mode=SplitInputMode()
        )
        return workflow

    async def dispatch(name, data, snapshot):
        dispatched.append(data)
        return data

    def driver():
        return StateDrivenExecutionDriver(
            graph=graph(),
            definition_version="v1",
            dispatcher=dispatch if remote_dispatch else None,
        )

    step = await driver().step(
        ExecutionSnapshot(
            "execution",
            "task",
            "graph",
            state={"start": "split", "input": ["a", "b"]},
        )
    )
    assert not step.completed
    assert step.state["queue"] == [["split", "a"], ["split", "b"]]
    assert dispatched == []
    # Reconstruct both the graph and execution state at every boundary.
    for _ in range(2):
        state = json.loads(json.dumps(step.state))
        step = await driver().step(
            ExecutionSnapshot("execution", "task", "graph", state=state)
        )
    assert step.completed
    assert dispatched == ["a", "b"]


async def test_callable_strategies_rebind_configuration_after_restart():
    from swarmauri_workflow_statedriven.join_strategies import conditional_join
    from swarmauri_workflow_statedriven.merge_strategies.custom_merge import (
        CustomMergeStrategy,
    )

    def graph():
        workflow = WorkflowBase()
        for name in ("start", "left", "right"):
            workflow.add_state(name, tool=IdentityTool())
        workflow.add_state(
            "join",
            tool=IdentityTool(),
            join_strategy=conditional_join.ConditionalJoinStrategy(
                lambda values: len(values) == 2
            ),
            merge_strategy=CustomMergeStrategy(
                lambda values: "+".join(values)
            ),
        )
        for source, target in (
            ("start", "left"),
            ("start", "right"),
            ("left", "join"),
            ("right", "join"),
        ):
            workflow.add_transition(source, target, Always())
        return workflow

    async def dispatch(name, data, snapshot):
        return data if name == "join" else name

    state = {"start": "start", "input": "brief"}
    for _ in range(4):
        driver = StateDrivenExecutionDriver(
            graph=graph(),
            definition_version="v1",
            dispatcher=dispatch,
        )
        step = await driver.step(
            ExecutionSnapshot("execution", "task", "graph", state=state)
        )
        state = json.loads(json.dumps(step.state))
        assert "predicate" not in state["strategies"]["join"]["join_strategy"]
        assert "fn" not in state["strategies"]["join"]["merge_strategy"]
    assert step.completed
    assert state["results"]["join"] == "left+right"
