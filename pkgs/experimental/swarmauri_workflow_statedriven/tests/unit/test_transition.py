# File: tests/workflows/test_transition.py

import pytest
from swarmauri_workflow_statedriven.transition import Transition
from swarmauri_workflow_statedriven.conditions.base import Condition


class TrueCondition(Condition):
    """
    Stub Condition that always returns True.
    """

    def evaluate(self, state):
        return True


class FalseCondition(Condition):
    """
    Stub Condition that always returns False.
    """

    def evaluate(self, state):
        return False


@pytest.mark.unit
def test_init_sets_attributes():
    """
    File: workflows/transition.py
    Class: Transition
    Method: __init__
    """
    cond = TrueCondition()
    t = Transition("A", "B", cond)
    assert t.source == "A"
    assert t.target == "B"
    assert t.condition is cond


@pytest.mark.unit
def test_is_triggered_returns_true_when_condition_true():
    """
    File: workflows/transition.py
    Class: Transition
    Method: is_triggered
    """
    cond = TrueCondition()
    t = Transition("src", "dst", cond)
    # state dict can be anything; TrueCondition ignores it
    assert t.is_triggered({"foo": "bar"}) is True


@pytest.mark.unit
def test_is_triggered_returns_false_when_condition_false():
    """
    File: workflows/transition.py
    Class: Transition
    Method: is_triggered
    """
    cond = FalseCondition()
    t = Transition("src", "dst", cond)
    assert t.is_triggered({"foo": "bar"}) is False
