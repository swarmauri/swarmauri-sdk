# File: tests/workflows/join_strategies/test_aggregator.py

import pytest
from swarmauri_workflow_statedriven.join_strategies.aggregator import AggregatorStrategy


@pytest.mark.unit
def test_init_creates_instance():
    """
    File: workflows/join_strategies/aggregator.py
    Class: AggregatorStrategy
    Method: __init__
    """
    strategy = AggregatorStrategy()
    assert isinstance(strategy, AggregatorStrategy)


@pytest.mark.unit
def test_is_satisfied_false_on_empty_buffer():
    """
    File: workflows/join_strategies/aggregator.py
    Class: AggregatorStrategy
    Method: is_satisfied
    """
    strategy = AggregatorStrategy()
    buffer = []
    assert strategy.is_satisfied(buffer) is False


@pytest.mark.unit
def test_is_satisfied_true_on_non_empty_buffer():
    """
    File: workflows/join_strategies/aggregator.py
    Class: AggregatorStrategy
    Method: is_satisfied
    """
    strategy = AggregatorStrategy()
    buffer = [1, 2, 3]
    assert strategy.is_satisfied(buffer) is True


@pytest.mark.unit
def test_aggregate_returns_copy_of_buffer():
    """
    File: workflows/join_strategies/aggregator.py
    Class: AggregatorStrategy
    Method: aggregate
    """
    strategy = AggregatorStrategy()
    original = ["a", "b", "c"]
    result = strategy.aggregate(original)
    # Should match content...
    assert result == original
    # ...but be a new list (shallow copy)
    assert result is not original


@pytest.mark.unit
def test_reset_does_not_affect_behavior():
    """
    File: workflows/join_strategies/aggregator.py
    Class: AggregatorStrategy
    Method: reset
    """
    strategy = AggregatorStrategy()
    # Populate a buffer and test satisfied
    buffer = [42]
    assert strategy.is_satisfied(buffer) is True
    # reset should not raise or change is_satisfied
    strategy.reset()
    assert strategy.is_satisfied(buffer) is True
