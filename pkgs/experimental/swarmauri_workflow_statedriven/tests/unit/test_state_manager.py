# File: tests/workflows/test_state_manager.py

import pytest
from swarmauri_workflow_statedriven.state_manager import StateManager
from swarmauri_workflow_statedriven.exceptions import WorkflowError


@pytest.mark.unit
def test_init():
    """
    File: workflows/state_manager.py
    Class: StateManager
    Method: __init__
    """
    sm = StateManager()
    assert sm.state == {}
    assert sm.logs == []
    assert sm.join_buffers == {}


@pytest.mark.unit
def test_update_and_get_state():
    """
    File: workflows/state_manager.py
    Class: StateManager
    Methods: update_state, get_state
    """
    sm = StateManager()
    sm.update_state("A", 42)
    assert sm.get_state("A") == 42


@pytest.mark.unit
def test_get_state_raises_when_missing():
    """
    File: workflows/state_manager.py
    Class: StateManager
    Method: get_state
    """
    sm = StateManager()
    with pytest.raises(WorkflowError):
        sm.get_state("unknown")


@pytest.mark.unit
def test_buffer_and_get_buffer():
    """
    File: workflows/state_manager.py
    Class: StateManager
    Methods: buffer_input, get_buffer
    """
    sm = StateManager()
    sm.buffer_input("T", "first")
    sm.buffer_input("T", "second")
    # get_buffer should return both items in order
    assert sm.get_buffer("T") == ["first", "second"]
    # get_buffer for unknown key returns empty list
    assert sm.get_buffer("nope") == []


@pytest.mark.unit
def test_pop_buffer_clears_buffer():
    """
    File: workflows/state_manager.py
    Class: StateManager
    Method: pop_buffer
    """
    sm = StateManager()
    sm.buffer_input("X", 1)
    sm.buffer_input("X", 2)
    # pop_buffer returns and clears
    popped = sm.pop_buffer("X")
    assert popped == [1, 2]
    assert sm.get_buffer("X") == []
    # pop_buffer on missing key returns empty list
    assert sm.pop_buffer("nope") == []


@pytest.mark.unit
def test_log_appends_messages():
    """
    File: workflows/state_manager.py
    Class: StateManager
    Method: log
    """
    sm = StateManager()
    sm.log("first message")
    sm.log("second message")
    assert sm.logs == ["first message", "second message"]
