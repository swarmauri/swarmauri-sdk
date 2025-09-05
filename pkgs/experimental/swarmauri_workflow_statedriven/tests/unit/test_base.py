# File: tests/workflows/test_base.py

import pytest
from swarmauri_workflow_statedriven.base import WorkflowBase
from swarmauri_workflow_statedriven.conditions.function_condition import (
    FunctionCondition,
)
from swarmauri_workflow_statedriven.exceptions import InvalidTransitionError


class DummyAgent:
    """
    Simple agent stub for testing.
    """

    def __init__(self, suffix: str = ""):
        self.suffix = suffix

    def exec(self, input_data):
        return f"{input_data}{self.suffix}"


def test_init():
    """
    Test WorkflowBase.__init__ initializes empty nodes, transitions, and state_manager.
    """
    wf = WorkflowBase()
    assert wf.nodes == {}
    assert wf.transitions == []
    # state_manager should start with empty state and logs
    assert wf.state_manager.state == {}
    assert wf.state_manager.logs == []


def test_add_state_errors():
    """
    Test WorkflowBase.add_state raises ValueError when neither or both agent/tool provided.
    """
    wf = WorkflowBase()
    with pytest.raises(ValueError):
        wf.add_state("no_backend")  # neither agent nor tool
    with pytest.raises(ValueError):
        wf.add_state(
            "both_backends", agent=DummyAgent(), tool=DummyAgent()
        )  # both provided


def test_add_state_success():
    """
    Test WorkflowBase.add_state registers a Node correctly (WorkflowBase.add_state).
    """
    wf = WorkflowBase()
    agent = DummyAgent()
    wf.add_state("A", agent=agent)
    assert "A" in wf.nodes
    node = wf.nodes["A"]
    # Node has correct name and agent
    assert node.name == "A"
    assert node.agent is agent


def test_add_transition_errors():
    """
    Test WorkflowBase.add_transition raises InvalidTransitionError on unknown states.
    """
    wf = WorkflowBase()
    with pytest.raises(InvalidTransitionError):
        wf.add_transition("X", "Y", FunctionCondition(lambda s: True))


def test_add_transition_success():
    """
    Test WorkflowBase.add_transition registers a Transition correctly (WorkflowBase.add_transition).
    """
    wf = WorkflowBase()
    wf.add_state("A", agent=DummyAgent())
    wf.add_state("B", agent=DummyAgent())
    cond = FunctionCondition(lambda s: True)
    wf.add_transition("A", "B", cond)
    assert len(wf.transitions) == 1
    t = wf.transitions[0]
    assert t.source == "A"
    assert t.target == "B"
    assert t.condition is cond


def test_run_linear():
    """
    Test WorkflowBase.run executes a simple linear workflow (WorkflowBase.run).
    """
    wf = WorkflowBase()
    start_agent = DummyAgent(suffix="_S")
    end_agent = DummyAgent(suffix="_E")
    wf.add_state("start", agent=start_agent)
    wf.add_state("end", agent=end_agent)
    wf.add_transition("start", "end", FunctionCondition(lambda s: True))

    results = wf.run("start", "data")
    # start.exec should append "_S", end.exec should append "_E"
    assert results["start"] == "data_S"
    assert results["end"] == "data_S_E"


def test_run_parallel_equivalence():
    """
    Test WorkflowBase.run_parallel matches WorkflowBase.run on a linear workflow (WorkflowBase.run_parallel).
    """
    wf = WorkflowBase()
    wf.add_state("X", agent=DummyAgent(suffix="1"))
    wf.add_state("Y", agent=DummyAgent(suffix="2"))
    wf.add_transition("X", "Y", FunctionCondition(lambda s: True))

    seq = wf.run("X", "foo")
    par = wf.run_parallel("X", "foo", max_workers=2)
    assert seq == par
