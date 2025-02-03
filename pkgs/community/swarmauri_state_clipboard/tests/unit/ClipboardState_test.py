import pytest
import pyperclip
from swarmauri_state_clipboard.ClipboardState import ClipboardState


@pytest.fixture
def clipboard_state():
    """
    Fixture to create a ClipboardState instance and clean up clipboard after tests.
    """
    # Store original clipboard content
    original_clipboard = pyperclip.paste()

    # Create ClipboardState
    state = ClipboardState()

    # Yield the state for tests to use
    yield state

    # Restore original clipboard content after tests
    pyperclip.copy(original_clipboard)


@pytest.mark.unit
def test_ubc_resource(clipboard_state):
    """
    Test the resource type of the ClipboardState.
    """
    assert clipboard_state.resource == "State"


@pytest.mark.unit
def test_write_and_read(clipboard_state):
    """
    Test writing data to clipboard and reading it back.
    """
    test_data = {"key1": "value1", "key2": 42}
    clipboard_state.write(test_data)
    read_data = clipboard_state.read()
    assert read_data == test_data


@pytest.mark.unit
def test_update(clipboard_state):
    """
    Test updating existing clipboard data.
    """
    # Initial write
    initial_data = {"existing_key": "existing_value"}
    clipboard_state.write(initial_data)

    # Update with new data
    update_data = {"new_key": "new_value"}
    clipboard_state.update(update_data)

    # Read and verify merged data
    read_data = clipboard_state.read()
    expected_data = {"existing_key": "existing_value", "new_key": "new_value"}
    assert read_data == expected_data


@pytest.mark.unit
def test_reset(clipboard_state):
    """
    Test resetting the clipboard state to an empty dictionary.
    """
    # Write some data
    clipboard_state.write({"some_key": "some_value"})

    # Reset
    clipboard_state.reset()

    # Verify empty state
    assert clipboard_state.read() == {}


@pytest.mark.unit
def test_deep_copy(clipboard_state):
    """
    Test creating a deep copy of the clipboard state.
    """
    # Write initial data
    initial_data = {"key1": "value1", "key2": "value2"}
    clipboard_state.write(initial_data)

    # Create deep copy
    copied_state = clipboard_state.deep_copy()

    # Verify copied state
    assert isinstance(copied_state, ClipboardState)
    assert copied_state.read() == initial_data
