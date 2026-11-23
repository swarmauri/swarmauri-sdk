# File: tests/workflows/merge_strategies/test_flatten_merge.py

import pytest
from swarmauri_workflow_statedriven.merge_strategies.flatten_merge import (
    FlattenMergeStrategy,
)


@pytest.mark.unit
def test_merge_empty_list_returns_empty_list():
    """
    File: workflows/merge_strategies/flatten_merge.py
    Class: FlattenMergeStrategy
    Method: merge
    """
    strategy = FlattenMergeStrategy()
    assert strategy.merge([]) == []


@pytest.mark.unit
def test_merge_list_of_lists_flattens_one_level():
    """
    File: workflows/merge_strategies/flatten_merge.py
    Class: FlattenMergeStrategy
    Method: merge
    """
    strategy = FlattenMergeStrategy()
    inp = [[1, 2], [3, 4]]
    result = strategy.merge(inp)
    assert result == [1, 2, 3, 4]


@pytest.mark.unit
def test_merge_mixed_scalars_and_lists():
    """
    File: workflows/merge_strategies/flatten_merge.py
    Class: FlattenMergeStrategy
    Method: merge
    """
    strategy = FlattenMergeStrategy()
    inp = ["a", [1, 2], "b", [], [3]]
    result = strategy.merge(inp)
    # "a" and "b" remain, inner lists flattened, empty lists contribute nothing
    assert result == ["a", 1, 2, "b", 3]


@pytest.mark.unit
def test_merge_nested_deeper_lists_only_flatten_top_level():
    """
    File: workflows/merge_strategies/flatten_merge.py
    Class: FlattenMergeStrategy
    Method: merge

    Only the first level of lists is flattened.
    """
    strategy = FlattenMergeStrategy()
    inp = [[[1], 2], [3, [4, 5]]]
    result = strategy.merge(inp)
    # inner lists [1] and [4,5] are not flattened further
    assert result == [[1], 2, 3, [4, 5]]


@pytest.mark.unit
def test_merge_non_list_items_appended_directly():
    """
    File: workflows/merge_strategies/flatten_merge.py
    Class: FlattenMergeStrategy
    Method: merge
    """
    strategy = FlattenMergeStrategy()

    class Custom:
        pass

    obj = Custom()
    inp = [obj, 42]
    result = strategy.merge(inp)
    assert result == [obj, 42]
