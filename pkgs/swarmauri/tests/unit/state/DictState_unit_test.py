import pytest
from swarmauri.state.concrete.DictState import DictState


@pytest.fixture
def dict_state():
    """
    Fixture to create a DictState instance for testing.
    """
    # Create DictState
    state = DictState()

    # Yield the state for tests to use
    yield state


@pytest.mark.unit
def test_resource_type(dict_state):
    """
    Test the resource type of the DictState.
    """
    assert dict_state.resource == "State"


@pytest.mark.unit
def test_write_and_read(dict_state):
    """
    Test writing data to DictState and reading it back.
    """
    test_data = {"key1": "value1", "key2": 42}
    dict_state.write(test_data)
    read_data = dict_state.read()
    assert read_data == test_data


@pytest.mark.unit
def test_update(dict_state):
    """
    Test updating existing DictState data.
    """
    # Initial write
    initial_data = {"existing_key": "existing_value"}
    dict_state.write(initial_data)

    # Update with new data
    update_data = {"new_key": "new_value"}
    dict_state.update(update_data)

    # Read and verify merged data
    read_data = dict_state.read()
    expected_data = {"existing_key": "existing_value", "new_key": "new_value"}
    assert read_data == expected_data


@pytest.mark.unit
def test_reset(dict_state):
    """
    Test resetting the DictState to an empty dictionary.
    """
    # Write some data
    dict_state.write({"some_key": "some_value"})

    # Reset
    dict_state.reset()

    # Verify empty state
    assert dict_state.read() == {}


@pytest.mark.unit
def test_deep_copy(dict_state):
    # Write initial data
    initial_data = {"key1": "value1", "key2": "value2"}
    dict_state.write(initial_data)

    # Create deep copy
    copied_state = dict_state.deep_copy()

    # Verify copied state
    assert isinstance(copied_state, DictState)
    assert copied_state.read() == initial_data

    # Verify deep copy by modifying original and copy independently
    dict_state.update({"new_key": "new_value"})
    assert copied_state.read() == initial_data  # Copy should remain unchanged
