# File: tests/workflows/merge_strategies/test_list_merge.py

import pytest
from swarmauri_workflow_statedriven.merge_strategies.list_merge import ListMergeStrategy


@pytest.mark.unit
def test_merge_empty_list_returns_empty_list():
    """
    File: workflows/merge_strategies/list_merge.py
    Class: ListMergeStrategy
    Method: merge
    """
    strategy = ListMergeStrategy()
    lst = []
    result = strategy.merge(lst)
    assert result == []
    # should return the same instance
    assert result is lst


@pytest.mark.unit
def test_merge_single_element_returns_same_list():
    """
    File: workflows/merge_strategies/list_merge.py
    Class: ListMergeStrategy
    Method: merge
    """
    strategy = ListMergeStrategy()
    lst = ["foo"]
    result = strategy.merge(lst)
    assert result == ["foo"]
    assert result is lst


@pytest.mark.unit
def test_merge_multiple_elements_returns_same_list():
    """
    File: workflows/merge_strategies/list_merge.py
    Class: ListMergeStrategy
    Method: merge
    """
    strategy = ListMergeStrategy()
    lst = [1, 2, 3]
    result = strategy.merge(lst)
    assert result == [1, 2, 3]
    assert result is lst


@pytest.mark.unit
def test_merge_list_of_lists_returns_same_structure():
    """
    File: workflows/merge_strategies/list_merge.py
    Class: ListMergeStrategy
    Method: merge
    """
    strategy = ListMergeStrategy()
    lst = [[1, 2], [3, 4]]
    result = strategy.merge(lst)
    assert result == [[1, 2], [3, 4]]
    assert result is lst


@pytest.mark.unit
def test_merge_mixed_types_returns_same_list():
    """
    File: workflows/merge_strategies/list_merge.py
    Class: ListMergeStrategy
    Method: merge
    """
    strategy = ListMergeStrategy()
    d = {"key": "value"}
    lst = ["a", 42, d, [1, 2]]
    result = strategy.merge(lst)
    assert result == ["a", 42, d, [1, 2]]
    assert result is lst
