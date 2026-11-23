# File: tests/workflows/merge_strategies/test_concat_merge.py

import pytest
from swarmauri_workflow_statedriven.merge_strategies.concat_merge import (
    ConcatMergeStrategy,
)


@pytest.mark.unit
def test_merge_empty_list_returns_empty_string():
    """
    File: workflows/merge_strategies/concat_merge.py
    Class: ConcatMergeStrategy
    Method: merge
    """
    strategy = ConcatMergeStrategy()
    assert strategy.merge([]) == ""


@pytest.mark.unit
def test_merge_single_element_returns_string_of_element():
    """
    File: workflows/merge_strategies/concat_merge.py
    Class: ConcatMergeStrategy
    Method: merge
    """
    strategy = ConcatMergeStrategy()
    # single string element
    assert strategy.merge(["foo"]) == "foo"
    # single non-string element
    assert strategy.merge([123]) == "123"


@pytest.mark.unit
def test_merge_multiple_elements_concatenates_in_order():
    """
    File: workflows/merge_strategies/concat_merge.py
    Class: ConcatMergeStrategy
    Method: merge
    """
    strategy = ConcatMergeStrategy()
    assert strategy.merge(["a", "b", "c"]) == "abc"


@pytest.mark.unit
def test_merge_mixed_types_stringifies_all():
    """
    File: workflows/merge_strategies/concat_merge.py
    Class: ConcatMergeStrategy
    Method: merge
    """
    strategy = ConcatMergeStrategy()
    # list containing string, int, dict, list
    result = strategy.merge(["x", 42, {"k": "v"}, [1, 2]])
    # string representation concatenation
    assert result == "x42{'k': 'v'}[1, 2]"


@pytest.mark.unit
def test_merge_nested_lists_uses_str_representation():
    """
    File: workflows/merge_strategies/concat_merge.py
    Class: ConcatMergeStrategy
    Method: merge
    """
    strategy = ConcatMergeStrategy()
    nested = [[1, 2], [3, 4]]
    merged = strategy.merge(nested)
    # Should be the string repr of each sub-list concatenated
    assert merged == "[1, 2][3, 4]"
