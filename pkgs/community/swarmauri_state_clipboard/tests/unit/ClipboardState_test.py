import pytest
from unittest.mock import patch
from swarmauri_state_clipboard.ClipboardState import ClipboardState


@pytest.fixture
def clipboard_state():
    """
    Fixture to create a ClipboardState instance with mocked clipboard operations.
    """
    mock_clipboard_content = ""

    def mock_copy(text):
        nonlocal mock_clipboard_content
        mock_clipboard_content = text

    def mock_paste():
        return mock_clipboard_content

    with (
        patch("pyperclip.copy", side_effect=mock_copy),
        patch("pyperclip.paste", side_effect=mock_paste),
    ):
        state = ClipboardState()
        yield state


@pytest.mark.unit
def test_ubc_resource(clipboard_state):
    """Test the resource type of the ClipboardState."""
    assert clipboard_state.resource == "State"


@pytest.mark.unit
def test_ubc_type(clipboard_state):
    assert clipboard_state.type == "ClipboardState"


@pytest.mark.unit
def test_serialization(clipboard_state):
    assert (
        clipboard_state.id
        == ClipboardState.model_validate_json(clipboard_state.model_dump_json()).id
    )


@pytest.mark.unit
def test_write_and_read(clipboard_state):
    """Test writing data to clipboard and reading it back."""
    test_data = {"key1": "value1", "key2": 42}
    clipboard_state.write(test_data)
    read_data = clipboard_state.read()
    assert read_data == test_data


@pytest.mark.unit
def test_update(clipboard_state):
    """Test updating existing clipboard data."""
    initial_data = {"existing_key": "existing_value"}
    clipboard_state.write(initial_data)

    update_data = {"new_key": "new_value"}
    clipboard_state.update(update_data)

    read_data = clipboard_state.read()
    expected_data = {"existing_key": "existing_value", "new_key": "new_value"}
    assert read_data == expected_data


@pytest.mark.unit
def test_reset(clipboard_state):
    """Test resetting the clipboard state."""
    clipboard_state.write({"some_key": "some_value"})
    clipboard_state.reset()
    assert clipboard_state.read() == {}


@pytest.mark.unit
def test_deep_copy(clipboard_state):
    """Test creating a deep copy of the clipboard state."""
    initial_data = {"key1": "value1", "key2": "value2"}
    clipboard_state.write(initial_data)

    copied_state = clipboard_state.deep_copy()

    assert isinstance(copied_state, ClipboardState)
    assert copied_state.read() == initial_data
