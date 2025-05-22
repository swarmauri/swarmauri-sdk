# File: tests/workflows/conditions/test_membership_condition.py

import pytest
from swarmauri_workflow_statedriven.conditions.membership_condition import (
    MembershipCondition,
)


@pytest.mark.unit
def test_init_sets_attributes():
    """
    File: workflows/conditions/membership_condition.py
    Class: MembershipCondition
    Method: __init__
    """
    cond = MembershipCondition(node_name="X", member=5, should_be_member=True)
    assert cond.node_name == "X"
    assert cond.member == 5
    assert cond.should_be_member is True


@pytest.mark.unit
def test_evaluate_true_when_member_present_and_should_be_member():
    """
    File: workflows/conditions/membership_condition.py
    Class: MembershipCondition
    Method: evaluate
    """
    cond = MembershipCondition(node_name="A", member="foo", should_be_member=True)
    state = {"A": ["foo", "bar"]}
    assert cond.evaluate(state) is True


@pytest.mark.unit
def test_evaluate_false_when_member_missing_and_should_be_member():
    """
    File: workflows/conditions/membership_condition.py
    Class: MembershipCondition
    Method: evaluate
    """
    cond = MembershipCondition(node_name="A", member="baz", should_be_member=True)
    state = {"A": ["foo", "bar"]}
    assert cond.evaluate(state) is False


@pytest.mark.unit
def test_evaluate_false_when_container_not_iterable_and_should_be_member():
    """
    File: workflows/conditions/membership_condition.py
    Class: MembershipCondition
    Method: evaluate

    Non-iterable container should yield False.
    """
    cond = MembershipCondition(node_name="B", member=1, should_be_member=True)
    state = {"B": 123}
    assert cond.evaluate(state) is False


@pytest.mark.unit
def test_evaluate_true_when_member_missing_and_should_not_be_member():
    """
    File: workflows/conditions/membership_condition.py
    Class: MembershipCondition
    Method: evaluate
    """
    cond = MembershipCondition(node_name="A", member="baz", should_be_member=False)
    state = {"A": ["foo", "bar"]}
    assert cond.evaluate(state) is True


@pytest.mark.unit
def test_evaluate_false_when_member_present_and_should_not_be_member():
    """
    File: workflows/conditions/membership_condition.py
    Class: MembershipCondition
    Method: evaluate
    """
    cond = MembershipCondition(node_name="A", member="foo", should_be_member=False)
    state = {"A": ["foo", "bar"]}
    assert cond.evaluate(state) is False


@pytest.mark.unit
def test_evaluate_false_when_node_missing_and_should_be_member():
    """
    File: workflows/conditions/membership_condition.py
    Class: MembershipCondition
    Method: evaluate

    Missing node yields False when should_be_member=True.
    """
    cond = MembershipCondition(node_name="Missing", member="x", should_be_member=True)
    state = {"Other": [1, 2, 3]}
    assert cond.evaluate(state) is False


@pytest.mark.unit
def test_evaluate_true_when_node_missing_and_should_not_be_member():
    """
    File: workflows/conditions/membership_condition.py
    Class: MembershipCondition
    Method: evaluate

    Missing node yields True when should_be_member=False.
    """
    cond = MembershipCondition(node_name="Missing", member="x", should_be_member=False)
    state = {"Other": ["x"]}
    assert cond.evaluate(state) is True
