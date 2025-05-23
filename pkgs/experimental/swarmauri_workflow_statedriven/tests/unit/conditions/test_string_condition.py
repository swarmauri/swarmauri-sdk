# File: tests/workflows/conditions/test_string_condition.py

import pytest
from swarmauri_workflow_statedriven.conditions.string_condition import StringCondition


@pytest.mark.unit
def test_contains_operator_true_and_false():
    """
    File: workflows/conditions/string_condition.py
    Class: StringCondition
    Method: evaluate with operator "contains"
    """
    cond = StringCondition(node_name="X", operator="contains", substring="foo")
    assert cond.evaluate({"X": "foobar"}) is True
    assert cond.evaluate({"X": "barbaz"}) is False


@pytest.mark.unit
def test_startswith_operator_true_and_false():
    """
    File: workflows/conditions/string_condition.py
    Class: StringCondition
    Method: evaluate with operator "startswith"
    """
    cond = StringCondition(node_name="Y", operator="startswith", substring="pre")
    assert cond.evaluate({"Y": "prefix"}) is True
    assert cond.evaluate({"Y": "suffix"}) is False


@pytest.mark.unit
def test_endswith_operator_true_and_false():
    """
    File: workflows/conditions/string_condition.py
    Class: StringCondition
    Method: evaluate with operator "endswith"
    """
    cond = StringCondition(node_name="Z", operator="endswith", substring="end")
    assert cond.evaluate({"Z": "the end"}) is True
    assert cond.evaluate({"Z": "the middle"}) is False


@pytest.mark.unit
def test_non_string_output_returns_false():
    """
    File: workflows/conditions/string_condition.py
    Class: StringCondition
    Method: evaluate
    """
    cond = StringCondition(node_name="X", operator="contains", substring="a")
    assert cond.evaluate({"X": 123}) is False
    # Missing key yields default "" which is str, contains yields False
    cond2 = StringCondition(node_name="Missing", operator="contains", substring="a")
    assert cond2.evaluate({}) is False


@pytest.mark.unit
def test_unsupported_operator_raises_value_error():
    """
    File: workflows/conditions/string_condition.py
    Class: StringCondition
    Method: evaluate with invalid operator
    """
    cond = StringCondition(node_name="X", operator="invalid", substring="x")
    with pytest.raises(ValueError):
        cond.evaluate({"X": "anything"})
