# File: tests/workflows/join_strategies/test_n_of_m_join.py

import pytest
from swarmauri_workflow_statedriven.join_strategies.n_of_m_join import NofMJoinStrategy


@pytest.mark.unit
def test_init_sets_n():
    """
    File: workflows/join_strategies/n_of_m_join.py
    Class: NofMJoinStrategy
    Method: __init__
    """
    strategy = NofMJoinStrategy(n=3)
    assert hasattr(strategy, "n")
    assert strategy.n == 3


@pytest.mark.unit
def test_is_satisfied_false_when_buffer_length_less_than_n():
    """
    File: workflows/join_strategies/n_of_m_join.py
    Class: NofMJoinStrategy
    Method: is_satisfied
    """
    strategy = NofMJoinStrategy(n=4)
    buffer = [1, 2, 3]
    assert strategy.is_satisfied(buffer) is False


@pytest.mark.unit
def test_is_satisfied_true_when_buffer_length_equals_n():
    """
    File: workflows/join_strategies/n_of_m_join.py
    Class: NofMJoinStrategy
    Method: is_satisfied
    """
    strategy = NofMJoinStrategy(n=2)
    buffer = ["a", "b"]
    assert strategy.is_satisfied(buffer) is True


@pytest.mark.unit
def test_is_satisfied_true_when_buffer_length_exceeds_n():
    """
    File: workflows/join_strategies/n_of_m_join.py
    Class: NofMJoinStrategy
    Method: is_satisfied
    """
    strategy = NofMJoinStrategy(n=2)
    buffer = [0, 1, 2]
    assert strategy.is_satisfied(buffer) is True


@pytest.mark.unit
def test_mark_complete_no_effect_and_no_error():
    """
    File: workflows/join_strategies/n_of_m_join.py
    Class: NofMJoinStrategy
    Method: mark_complete
    """
    strategy = NofMJoinStrategy(n=1)
    # mark_complete should not raise and not alter behavior
    strategy.mark_complete("branchX")
    assert strategy.is_satisfied([]) is False
    assert strategy.is_satisfied([42]) is True


@pytest.mark.unit
def test_reset_no_internal_state_change():
    """
    File: workflows/join_strategies/n_of_m_join.py
    Class: NofMJoinStrategy
    Method: reset
    """
    strategy = NofMJoinStrategy(n=5)
    # reset should not change n or behavior
    strategy.reset()
    assert strategy.n == 5
    buffer = list(range(5))
    assert strategy.is_satisfied(buffer) is True
