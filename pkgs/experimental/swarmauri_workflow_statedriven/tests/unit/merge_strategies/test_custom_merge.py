# File: tests/workflows/merge_strategies/test_custom_merge.py

import pytest
from swarmauri_workflow_statedriven.merge_strategies.custom_merge import (
    CustomMergeStrategy,
)


def sample_fn(inputs):
    # Example: return the count of inputs
    return len(inputs)


@pytest.mark.unit
def test_init_sets_function():
    """
    File: workflows/merge_strategies/custom_merge.py
    Class: CustomMergeStrategy
    Method: __init__
    """
    strategy = CustomMergeStrategy(sample_fn)
    assert strategy.fn is sample_fn


@pytest.mark.unit
def test_merge_applies_function_to_inputs():
    """
    File: workflows/merge_strategies/custom_merge.py
    Class: CustomMergeStrategy
    Method: merge
    """
    strategy = CustomMergeStrategy(sample_fn)
    # Passing a list of three items should return 3
    result = strategy.merge([1, 2, 3])
    assert result == 3


@pytest.mark.unit
def test_merge_with_empty_list():
    """
    File: workflows/merge_strategies/custom_merge.py
    Class: CustomMergeStrategy
    Method: merge
    """
    strategy = CustomMergeStrategy(sample_fn)
    # Empty input list → sample_fn returns 0
    assert strategy.merge([]) == 0


@pytest.mark.unit
def test_merge_propagates_exception_from_fn():
    """
    File: workflows/merge_strategies/custom_merge.py
    Class: CustomMergeStrategy
    Method: merge
    """

    def error_fn(_):
        raise RuntimeError("merge error")

    strategy = CustomMergeStrategy(error_fn)
    with pytest.raises(RuntimeError) as exc:
        strategy.merge([42])
    assert "merge error" in str(exc.value)
