# File: tests/workflows/merge_strategies/test_identity_merge.py

import pytest
from swarmauri_workflow_statedriven.merge_strategies.identity_merge import (
    IdentityMergeStrategy,
)


@pytest.mark.unit
def test_merge_returns_same_list_instance():
    """
    File: workflows/merge_strategies/identity_merge.py
    Class: IdentityMergeStrategy
    Method: merge

    When inputs is a list, merge should return the same list object.
    """
    strategy = IdentityMergeStrategy()
    data = [1, 2, 3]
    result = strategy.merge(data)
    assert result is data


@pytest.mark.unit
def test_merge_returns_same_dict_instance():
    """
    File: workflows/merge_strategies/identity_merge.py
    Class: IdentityMergeStrategy
    Method: merge

    When inputs is a dict, merge should return the same dict object.
    """
    strategy = IdentityMergeStrategy()
    data = {"a": 1}
    result = strategy.merge(data)
    assert result is data


@pytest.mark.unit
def test_merge_returns_same_scalar():
    """
    File: workflows/merge_strategies/identity_merge.py
    Class: IdentityMergeStrategy
    Method: merge

    When inputs is a scalar (int or str), merge should return it unchanged.
    """
    strategy = IdentityMergeStrategy()
    for scalar in [42, "foo", None]:
        result = strategy.merge(scalar)
        assert result is scalar


@pytest.mark.unit
def test_merge_returns_same_complex_object():
    """
    File: workflows/merge_strategies/identity_merge.py
    Class: IdentityMergeStrategy
    Method: merge

    When inputs is an arbitrary object, merge should return it unchanged.
    """

    class Custom:
        pass

    strategy = IdentityMergeStrategy()
    obj = Custom()
    result = strategy.merge(obj)
    assert result is obj
