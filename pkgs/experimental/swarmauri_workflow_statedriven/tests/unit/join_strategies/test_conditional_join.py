# File: tests/workflows/join_strategies/test_conditional_join.py

import pytest
from swarmauri_workflow_statedriven.join_strategies.conditional_join import (
    ConditionalJoinStrategy,
)


@pytest.mark.unit
def test_init_sets_predicate():
    """
    File: workflows/join_strategies/conditional_join.py
    Class: ConditionalJoinStrategy
    Method: __init__
    """

    def predicate(buf):
        return True

    strategy = ConditionalJoinStrategy(predicate)
    # The predicate attribute should be set to the provided function
    assert strategy.predicate is predicate


@pytest.mark.unit
def test_is_satisfied_true_when_predicate_true():
    """
    File: workflows/join_strategies/conditional_join.py
    Class: ConditionalJoinStrategy
    Method: is_satisfied
    """

    def predicate(buf):
        return len(buf) >= 2

    strategy = ConditionalJoinStrategy(predicate)
    assert strategy.is_satisfied([1, 2]) is True
    assert strategy.is_satisfied([0, 1, 2, 3]) is True


@pytest.mark.unit
def test_is_satisfied_false_when_predicate_false():
    """
    File: workflows/join_strategies/conditional_join.py
    Class: ConditionalJoinStrategy
    Method: is_satisfied
    """

    def predicate(buf):
        return "ready" in buf

    strategy = ConditionalJoinStrategy(predicate)
    assert strategy.is_satisfied([]) is False
    assert strategy.is_satisfied(["not-ready"]) is False


@pytest.mark.unit
def test_mark_complete_no_error_and_no_effect():
    """
    File: workflows/join_strategies/conditional_join.py
    Class: ConditionalJoinStrategy
    Method: mark_complete
    """

    def always_true(buf):
        return True

    strategy = ConditionalJoinStrategy(always_true)
    # mark_complete is a no-op and should not raise
    strategy.mark_complete("any_branch")
    # is_satisfied remains governed by predicate
    assert strategy.is_satisfied([]) is True


@pytest.mark.unit
def test_reset_no_error_and_predicate_unchanged():
    """
    File: workflows/join_strategies/conditional_join.py
    Class: ConditionalJoinStrategy
    Method: reset
    """
    calls = []

    def pred(buf):
        calls.append(list(buf))
        return False

    strategy = ConditionalJoinStrategy(pred)
    # call before reset
    strategy.is_satisfied([1])
    # reset should not raise or alter predicate
    strategy.reset()
    strategy.is_satisfied([2, 3])
    # predicate was invoked on both buffers
    assert calls == [[1], [2, 3]]
