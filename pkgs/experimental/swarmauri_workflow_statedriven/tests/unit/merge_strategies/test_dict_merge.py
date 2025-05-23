# File: tests/workflows/merge_strategies/test_dict_merge.py

import pytest
from swarmauri_workflow_statedriven.merge_strategies.dict_merge import DictMergeStrategy


@pytest.mark.unit
def test_merge_empty_list_returns_empty_dict():
    """
    File: workflows/merge_strategies/dict_merge.py
    Class: DictMergeStrategy
    Method: merge
    """
    strategy = DictMergeStrategy()
    assert strategy.merge([]) == {}


@pytest.mark.unit
def test_merge_single_dict_returns_same_dict():
    """
    File: workflows/merge_strategies/dict_merge.py
    Class: DictMergeStrategy
    Method: merge
    """
    strategy = DictMergeStrategy()
    d = {"a": 1}
    result = strategy.merge([d])
    assert result == {"a": 1}
    # should be a new dict, not the same instance
    assert result is not d


@pytest.mark.unit
def test_merge_multiple_dicts_combines_keys():
    """
    File: workflows/merge_strategies/dict_merge.py
    Class: DictMergeStrategy
    Method: merge
    """
    strategy = DictMergeStrategy()
    d1 = {"x": 1}
    d2 = {"y": 2}
    result = strategy.merge([d1, d2])
    assert result == {"x": 1, "y": 2}


@pytest.mark.unit
def test_merge_overlapping_keys_last_wins():
    """
    File: workflows/merge_strategies/dict_merge.py
    Class: DictMergeStrategy
    Method: merge
    """
    strategy = DictMergeStrategy()
    d1 = {"k": "first"}
    d2 = {"k": "second", "other": 3}
    result = strategy.merge([d1, d2])
    assert result == {"k": "second", "other": 3}


@pytest.mark.unit
def test_merge_ignores_non_dict_items():
    """
    File: workflows/merge_strategies/dict_merge.py
    Class: DictMergeStrategy
    Method: merge
    """
    strategy = DictMergeStrategy()
    d = {"a": 1}
    result = strategy.merge([d, 123, "foo", {"b": 2}])
    assert result == {"a": 1, "b": 2}


@pytest.mark.unit
def test_merge_shallow_merges_nested_dicts():
    """
    File: workflows/merge_strategies/dict_merge.py
    Class: DictMergeStrategy
    Method: merge

    Confirms that nested dict values are replaced wholesale (shallow merge).
    """
    strategy = DictMergeStrategy()
    d1 = {"n": {"i": 1}}
    d2 = {"n": {"j": 2}}
    result = strategy.merge([d1, d2])
    # shallow merge: 'n' key from d2 replaces d1's value entirely
    assert result == {"n": {"j": 2}}
