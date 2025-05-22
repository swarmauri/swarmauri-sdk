# File: tests/workflows/join_strategies/test_first_join.py

import pytest
from swarmauri_workflow_statedriven.join_strategies.first_join import FirstJoinStrategy


@pytest.mark.unit
def test_init_sets_completed_false():
    """
    File: workflows/join_strategies/first_join.py
    Class: FirstJoinStrategy
    Method: __init__
    """
    strategy = FirstJoinStrategy()
    # internal flag _completed should start False
    assert not getattr(strategy, "_completed", False)


@pytest.mark.unit
def test_is_satisfied_false_before_any_arrival_and_empty_buffer():
    """
    File: workflows/join_strategies/first_join.py
    Class: FirstJoinStrategy
    Method: is_satisfied
    """
    strategy = FirstJoinStrategy()
    # no arrivals, empty buffer => not satisfied
    assert strategy.is_satisfied([]) is False


@pytest.mark.unit
def test_is_satisfied_true_when_buffer_non_empty_even_without_mark_complete():
    """
    File: workflows/join_strategies/first_join.py
    Class: FirstJoinStrategy
    Method: is_satisfied
    """
    strategy = FirstJoinStrategy()
    # even without mark_complete, a non-empty buffer should satisfy
    assert strategy.is_satisfied([1]) is True


@pytest.mark.unit
def test_mark_complete_sets_completed_and_satisfies_empty_buffer():
    """
    File: workflows/join_strategies/first_join.py
    Class: FirstJoinStrategy
    Methods: mark_complete, is_satisfied
    """
    strategy = FirstJoinStrategy()
    strategy.mark_complete("branch1")
    # after first arrival, empty buffer is considered satisfied
    assert strategy.is_satisfied([]) is True


@pytest.mark.unit
def test_mark_complete_idempotent():
    """
    File: workflows/join_strategies/first_join.py
    Class: FirstJoinStrategy
    Methods: mark_complete, is_satisfied
    """
    strategy = FirstJoinStrategy()
    strategy.mark_complete("branch1")
    strategy.mark_complete("branch2")
    # still satisfied after multiple arrivals
    assert strategy.is_satisfied([]) is True


@pytest.mark.unit
def test_reset_clears_completed_flag():
    """
    File: workflows/join_strategies/first_join.py
    Class: FirstJoinStrategy
    Method: reset
    """
    strategy = FirstJoinStrategy()
    strategy.mark_complete("branch1")
    strategy.reset()
    # after reset, with empty buffer it's no longer satisfied
    assert strategy.is_satisfied([]) is False
    # but a non-empty buffer still satisfies via buffer length
    assert strategy.is_satisfied([42]) is True
