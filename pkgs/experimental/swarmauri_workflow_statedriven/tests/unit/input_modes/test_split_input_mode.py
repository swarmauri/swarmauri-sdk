# File: tests/workflows/input_modes/test_split_input_mode.py

import pytest
from swarmauri_workflow_statedriven.input_modes.split import SplitInputMode


class DummyStateManager:
    """
    Stub state manager that records enqueued items.
    """

    def __init__(self):
        self.enqueued = []

    def enqueue(self, item):
        self.enqueued.append(item)


@pytest.mark.unit
def test_prepare_splits_list_and_enqueues_elements():
    """
    File: workflows/input_modes/split.py
    Class: SplitInputMode
    Method: prepare

    When data is a non-empty list, prepare should enqueue each element
    and return None to skip direct execution.
    """
    mode = SplitInputMode()
    sm = DummyStateManager()
    data = ["x", "y", "z"]
    result = mode.prepare(state_manager=sm, node_name="N", data=data, results={})
    # prepare returns None
    assert result is None
    # enqueue should have been called for each element with the tuple (node_name, element)
    assert sm.enqueued == [("N", "x"), ("N", "y"), ("N", "z")]


@pytest.mark.unit
def test_prepare_returns_data_for_non_list_inputs():
    """
    File: workflows/input_modes/split.py
    Class: SplitInputMode
    Method: prepare

    When data is not a list, prepare should return it unchanged.
    """
    mode = SplitInputMode()
    sm = DummyStateManager()
    for scalar in [123, "foo", {"a": 1}]:
        result = mode.prepare(state_manager=sm, node_name="N", data=scalar, results={})
        assert result == scalar
    # ensure no enqueues happened
    assert sm.enqueued == []
