# File: tests/workflows/conditions/test_function_condition.py

import pytest
from swarmauri_workflow_statedriven.conditions.function_condition import (
    FunctionCondition,
)


@pytest.mark.unit
def test_init_sets_callable():
    """
    File: workflows/conditions/function_condition.py
    Class: FunctionCondition
    Method: __init__
    """

    def fn(s):
        return "key" in s

    cond = FunctionCondition(fn)
    assert cond.fn is fn


@pytest.mark.unit
def test_evaluate_returns_true_when_fn_true():
    """
    File: workflows/conditions/function_condition.py
    Class: FunctionCondition
    Method: evaluate
    """

    def fn(state):
        return state.get("x", 0) > 0

    cond = FunctionCondition(fn)
    assert cond.evaluate({"x": 5}) is True


@pytest.mark.unit
def test_evaluate_returns_false_when_fn_false():
    """
    File: workflows/conditions/function_condition.py
    Class: FunctionCondition
    Method: evaluate
    """

    def fn(state):
        return False

    cond = FunctionCondition(fn)
    assert cond.evaluate({"any": "value"}) is False


@pytest.mark.unit
def test_evaluate_propagates_exceptions():
    """
    File: workflows/conditions/function_condition.py
    Class: FunctionCondition
    Method: evaluate

    If the wrapped function raises, evaluate should propagate the error.
    """

    def error_fn(_):
        raise RuntimeError("oops")

    cond = FunctionCondition(error_fn)
    with pytest.raises(RuntimeError) as exc:
        cond.evaluate({})
    assert "oops" in str(exc.value)
