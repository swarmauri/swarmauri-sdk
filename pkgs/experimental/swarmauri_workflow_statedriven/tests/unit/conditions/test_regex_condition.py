# File: tests/workflows/conditions/test_regex_condition.py

import pytest
import re
from swarmauri_workflow_statedriven.conditions.regex_condition import RegexCondition


@pytest.mark.unit
def test_init_compiles_pattern():
    """
    File: workflows/conditions/regex_condition.py
    Class: RegexCondition
    Method: __init__
    """
    cond = RegexCondition(node_name="X", pattern=r"\d+")
    # regex attribute should be a compiled pattern
    assert hasattr(cond, "regex")
    assert isinstance(cond.regex, re.Pattern)
    assert cond.node_name == "X"


@pytest.mark.unit
def test_init_invalid_pattern_raises_error():
    """
    File: workflows/conditions/regex_condition.py
    Class: RegexCondition
    Method: __init__

    Passing a malformed regex should raise a re.error.
    """
    with pytest.raises(re.error):
        RegexCondition(node_name="X", pattern="*[")  # invalid regex


@pytest.mark.unit
def test_evaluate_true_when_pattern_matches():
    """
    File: workflows/conditions/regex_condition.py
    Class: RegexCondition
    Method: evaluate

    Should return True if the pattern is found in the node's output.
    """
    cond = RegexCondition(node_name="A", pattern=r"hello")
    state = {"A": "well, hello there"}
    assert cond.evaluate(state) is True


@pytest.mark.unit
def test_evaluate_false_when_pattern_not_matches():
    """
    File: workflows/conditions/regex_condition.py
    Class: RegexCondition
    Method: evaluate

    Should return False if the pattern is not found.
    """
    cond = RegexCondition(node_name="A", pattern=r"\d{3}")
    state = {"A": "no digits here"}
    assert cond.evaluate(state) is False


@pytest.mark.unit
def test_evaluate_false_when_output_not_string():
    """
    File: workflows/conditions/regex_condition.py
    Class: RegexCondition
    Method: evaluate

    Non-string outputs should yield False.
    """
    cond = RegexCondition(node_name="B", pattern="x")
    state = {"B": 12345}
    assert cond.evaluate(state) is False


@pytest.mark.unit
def test_evaluate_false_when_node_missing():
    """
    File: workflows/conditions/regex_condition.py
    Class: RegexCondition
    Method: evaluate

    Missing node key yields False.
    """
    cond = RegexCondition(node_name="Missing", pattern=".*")
    state = {"Other": "value"}
    assert cond.evaluate(state) is False
