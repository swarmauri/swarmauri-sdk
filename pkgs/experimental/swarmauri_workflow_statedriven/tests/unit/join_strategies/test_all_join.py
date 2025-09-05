# File: tests/workflows/join_strategies/test_all_join.py

import pytest
from swarmauri_workflow_statedriven.join_strategies.all_join import AllJoinStrategy


@pytest.mark.unit
def test_init_has_zero_expected_count():
    """
    File: workflows/join_strategies/all_join.py
    Class: AllJoinStrategy
    Method: __init__
    """
    strategy = AllJoinStrategy()
    # expected_count should default to 0 before configuration
    assert hasattr(strategy, "expected_count")
    assert strategy.expected_count == 0


@pytest.mark.unit
def test_configure_sets_expected_count():
    """
    File: workflows/join_strategies/all_join.py
    Class: AllJoinStrategy
    Method: configure
    """
    strategy = AllJoinStrategy()
    strategy.configure(expected_count=3)
    assert strategy.expected_count == 3


@pytest.mark.unit
def test_is_satisfied_false_when_buffer_less_than_configured():
    """
    File: workflows/join_strategies/all_join.py
    Class: AllJoinStrategy
    Method: is_satisfied
    """
    strategy = AllJoinStrategy()
    strategy.configure(expected_count=4)
    buffer = [1, 2, 3]
    assert strategy.is_satisfied(buffer) is False


@pytest.mark.unit
def test_is_satisfied_true_when_buffer_equals_configured():
    """
    File: workflows/join_strategies/all_join.py
    Class: AllJoinStrategy
    Method: is_satisfied
    """
    strategy = AllJoinStrategy()
    strategy.configure(expected_count=2)
    buffer = ["a", "b"]
    assert strategy.is_satisfied(buffer) is True


@pytest.mark.unit
def test_is_satisfied_true_when_buffer_exceeds_configured():
    """
    File: workflows/join_strategies/all_join.py
    Class: AllJoinStrategy
    Method: is_satisfied
    """
    strategy = AllJoinStrategy()
    strategy.configure(expected_count=2)
    buffer = [0, 1, 2]
    assert strategy.is_satisfied(buffer) is True


@pytest.mark.unit
def test_mark_complete_no_effect():
    """
    File: workflows/join_strategies/all_join.py
    Class: AllJoinStrategy
    Method: mark_complete

    mark_complete should not alter expected_count or satisfaction logic.
    """
    strategy = AllJoinStrategy()
    strategy.configure(expected_count=1)
    strategy.mark_complete("any_branch")
    # still governed by buffer length vs expected_count
    assert strategy.expected_count == 1
    assert strategy.is_satisfied([]) is False
    assert strategy.is_satisfied([42]) is True


@pytest.mark.unit
def test_reset_does_not_change_expected_count():
    """
    File: workflows/join_strategies/all_join.py
    Class: AllJoinStrategy
    Method: reset

    reset should not alter expected_count.
    """
    strategy = AllJoinStrategy()
    strategy.configure(expected_count=5)
    strategy.reset()
    assert strategy.expected_count == 5
    # behavior remains same
    buffer = list(range(5))
    assert strategy.is_satisfied(buffer) is True
