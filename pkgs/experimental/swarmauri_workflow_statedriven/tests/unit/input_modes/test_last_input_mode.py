# File: tests/workflows/input_modes/test_last_input_mode.py

import pytest
from swarmauri_workflow_statedriven.input_modes.last import LastInputMode


@pytest.mark.unit
def test_prepare_returns_last_element_for_non_empty_list():
    """
    File: workflows/input_modes/last.py
    Class: LastInputMode
    Method: prepare

    Should return the last element of a non-empty list.
    """
    mode = LastInputMode()
    data = ["a", "b", "c"]
    result = mode.prepare(state_manager=None, node_name="X", data=data, results={})
    assert result == "c"


@pytest.mark.unit
def test_prepare_returns_none_for_empty_list():
    """
    File: workflows/input_modes/last.py
    Class: LastInputMode
    Method: prepare

    Should return None when the list is empty.
    """
    mode = LastInputMode()
    result = mode.prepare(state_manager=None, node_name="X", data=[], results={})
    assert result is None


@pytest.mark.unit
def test_prepare_passes_through_scalar():
    """
    File: workflows/input_modes/last.py
    Class: LastInputMode
    Method: prepare

    Should return the data unchanged when it is not a list.
    """
    mode = LastInputMode()
    for scalar in [42, "foo", {"k": "v"}]:
        result = mode.prepare(
            state_manager=None, node_name="X", data=scalar, results={}
        )
        assert result == scalar
