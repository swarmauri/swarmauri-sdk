# File: tests/workflows/conditions/test_base_condition.py

import pytest
from swarmauri_workflow_statedriven.conditions.base import Condition


@pytest.mark.unit
def test_condition_is_abstract():
    """
    File: workflows/conditions/base.py
    Class: Condition
    Method: evaluate (abstract)

    Ensure that Condition cannot be instantiated directly.
    """
    with pytest.raises(TypeError):
        Condition()


class DummyCondition(Condition):
    """
    Concrete subclass implementing evaluate for testing.
    """

    def __init__(self, result):
        self.result = result

    def evaluate(self, state):
        return self.result


@pytest.mark.unit
def test_dummy_condition_evaluate_returns_provided_result():
    """
    File: workflows/conditions/base.py
    Class: DummyCondition (subclass of Condition)
    Method: evaluate
    """
    true_cond = DummyCondition(True)
    false_cond = DummyCondition(False)
    assert true_cond.evaluate({}) is True
    assert false_cond.evaluate({"any": "state"}) is False
