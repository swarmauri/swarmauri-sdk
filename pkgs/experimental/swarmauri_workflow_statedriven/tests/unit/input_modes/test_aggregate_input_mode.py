# File: tests/workflows/input_modes/test_aggregate_input_mode.py

import pytest
from swarmauri_workflow_statedriven.input_modes.aggregate import AggregateInputMode


class DummyStateManager:
    """
    Stub state manager (not used by AggregateInputMode).
    """

    pass


@pytest.mark.unit
def test_prepare_returns_shallow_copy_of_results():
    """
    File: workflows/input_modes/aggregate.py
    Class: AggregateInputMode
    Method: prepare

    Should return a shallow copy of the results dict.
    """
    mode = AggregateInputMode()
    sm = DummyStateManager()
    results = {"A": 1, "B": [2, 3]}
    prepared = mode.prepare(
        state_manager=sm, node_name="X", data="ignored", results=results
    )
    # returned dict equal to original
    assert prepared == results
    # but not the same object
    assert prepared is not results


@pytest.mark.unit
def test_modifying_prepared_does_not_mutate_original():
    """
    File: workflows/input_modes/aggregate.py
    Class: AggregateInputMode
    Method: prepare

    Verify that changes to prepared copy do not affect the original results.
    """
    mode = AggregateInputMode()
    sm = DummyStateManager()
    results = {"A": {"nested": 9}}
    prepared = mode.prepare(state_manager=sm, node_name="X", data=None, results=results)
    # mutate prepared
    prepared["A"] = "changed"
    # original remains unchanged
    assert results["A"] == {"nested": 9}


@pytest.mark.unit
def test_prepare_ignores_data_parameter():
    """
    File: workflows/input_modes/aggregate.py
    Class: AggregateInputMode
    Method: prepare

    The 'data' argument should have no effect on the returned value.
    """
    mode = AggregateInputMode()
    sm = DummyStateManager()
    results = {"key": "value"}
    # Try with various data inputs
    for data in [None, 123, "foo", [1, 2, 3]]:
        prepared = mode.prepare(
            state_manager=sm, node_name="X", data=data, results=results
        )
        assert prepared == results
