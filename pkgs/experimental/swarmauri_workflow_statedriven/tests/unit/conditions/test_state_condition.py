# File: tests/workflows/conditions/test_state_condition.py

import pytest
from swarmauri_workflow_statedriven.conditions.state_condition import (
    StateValueCondition,
)


@pytest.mark.unit
def test_eq_comparator_true_and_false():
    """
    File: workflows/conditions/state_condition.py
    Class: StateValueCondition
    Method: evaluate
    """
    cond_true = StateValueCondition(node_name="X", expected=5, comparator="eq")
    assert cond_true.evaluate({"X": 5}) is True
    assert cond_true.evaluate({"X": 4}) is False


@pytest.mark.unit
def test_ne_comparator_true_and_false():
    cond_true = StateValueCondition(node_name="X", expected=5, comparator="ne")
    assert cond_true.evaluate({"X": 4}) is True
    assert cond_true.evaluate({"X": 5}) is False


@pytest.mark.unit
def test_gt_comparator():
    cond = StateValueCondition(node_name="X", expected=10, comparator="gt")
    assert cond.evaluate({"X": 11}) is True
    assert cond.evaluate({"X": 10}) is False
    assert cond.evaluate({"X": 9}) is False


@pytest.mark.unit
def test_lt_comparator():
    cond = StateValueCondition(node_name="X", expected=10, comparator="lt")
    assert cond.evaluate({"X": 9}) is True
    assert cond.evaluate({"X": 10}) is False
    assert cond.evaluate({"X": 11}) is False


@pytest.mark.unit
def test_ge_comparator():
    cond = StateValueCondition(node_name="X", expected=10, comparator="ge")
    assert cond.evaluate({"X": 10}) is True
    assert cond.evaluate({"X": 11}) is True
    assert cond.evaluate({"X": 9}) is False


@pytest.mark.unit
def test_le_comparator():
    cond = StateValueCondition(node_name="X", expected=10, comparator="le")
    assert cond.evaluate({"X": 10}) is True
    assert cond.evaluate({"X": 9}) is True
    assert cond.evaluate({"X": 11}) is False


@pytest.mark.unit
def test_missing_node_returns_none_comparisons_false():
    cond = StateValueCondition(node_name="Missing", expected=1, comparator="eq")
    # state.get returns None, None == 1 is False
    assert cond.evaluate({}) is False


@pytest.mark.unit
def test_unsupported_comparator_raises():
    cond = StateValueCondition(node_name="X", expected=1, comparator="unknown")
    with pytest.raises(ValueError):
        cond.evaluate({"X": 1})
