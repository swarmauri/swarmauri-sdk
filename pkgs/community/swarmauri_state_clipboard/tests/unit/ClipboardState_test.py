"""
This module contains unit tests for the ClipboardState class, which uses
the system clipboard to store and retrieve state data. The tests verify
the functionality of reading, writing, updating, resetting, and making
deep copies of the clipboard state. Additionally, tests ensure that the
class methods for copying and pasting text to/from the clipboard work as
expected under mocked conditions.
"""

from unittest.mock import patch

import pytest
from swarmauri_state_clipboard.ClipboardState import ClipboardState


@pytest.fixture
def clipboard_state():
    """
    Create a ClipboardState instance with mocked clipboard methods.
    """
    mock_clipboard_content = ""

    # Fix: Updated mock functions to match the correct signatures
    def mock_paste(text: str) -> None:  # Must accept a text parameter
        nonlocal mock_clipboard_content
        mock_clipboard_content = text

    def mock_copy() -> str:  # No parameters, returns the content
        return mock_clipboard_content

    with (
        patch.object(ClipboardState, "clipboard_paste", side_effect=mock_paste),
        patch.object(ClipboardState, "clipboard_copy", side_effect=mock_copy),
    ):
        state = ClipboardState()
        yield state


@pytest.mark.unit
def test_ubc_resource(clipboard_state):
    """
    Test that the resource type of the ClipboardState is 'State'.

    clipboard_state (ClipboardState): The ClipboardState fixture instance.

    RETURNS (None): Raises an assertion if the resource does not match "State".
    """
    assert clipboard_state.resource == "State"


@pytest.mark.unit
def test_ubc_type(clipboard_state):
    """
    Test that the type of the ClipboardState is 'ClipboardState'.

    clipboard_state (ClipboardState): The ClipboardState fixture instance.

    RETURNS (None): Raises an assertion if the type does not match "ClipboardState".
    """
    assert clipboard_state.type == "ClipboardState"


@pytest.mark.unit
def test_serialization(clipboard_state):
    """
    Test that a ClipboardState can be serialized and deserialized properly.

    Verifies that a state instance, when serialized to JSON and then deserialized,
    retains the same identifier.

    clipboard_state (ClipboardState): The ClipboardState fixture instance.

    RETURNS (None): Raises an assertion if the ID changes after serialization
        and deserialization.
    """
    assert (
        clipboard_state.id
        == ClipboardState.model_validate_json(clipboard_state.model_dump_json()).id
    )


@pytest.mark.unit
def test_write_and_read(clipboard_state):
    """
    Test writing data to the clipboard and reading it back.

    clipboard_state (ClipboardState): The ClipboardState fixture instance.

    RETURNS (None): Raises an assertion if the data read from the clipboard
        does not match the data that was written.
    """
    test_data = {"key1": "value1", "key2": 42}
    clipboard_state.write(test_data)
    read_data = clipboard_state.read()
    assert read_data == test_data


@pytest.mark.unit
def test_update(clipboard_state):
    """
    Test updating existing clipboard data by merging with new data.

    1. Write initial data to the clipboard.
    2. Update with new data.
    3. Verify the merged data is correct.

    clipboard_state (ClipboardState): The ClipboardState fixture instance.

    RETURNS (None): Raises an assertion if the merged data does not match expectations.
    """
    initial_data = {"existing_key": "existing_value"}
    clipboard_state.write(initial_data)

    update_data = {"new_key": "new_value"}
    clipboard_state.update(update_data)

    read_data = clipboard_state.read()
    expected_data = {"existing_key": "existing_value", "new_key": "new_value"}
    assert read_data == expected_data


@pytest.mark.unit
def test_reset(clipboard_state):
    """
    Test resetting the clipboard state to an empty dictionary.

    clipboard_state (ClipboardState): The ClipboardState fixture instance.

    RETURNS (None): Raises an assertion if the read data after reset is not empty.
    """
    clipboard_state.write({"some_key": "some_value"})
    clipboard_state.reset()
    assert clipboard_state.read() == {}


@pytest.mark.unit
def test_deep_copy(clipboard_state):
    """
    Test creating a deep copy of the current clipboard state.

    Verifies that the copied state's data matches the original state
    while confirming it's a separate ClipboardState instance.

    clipboard_state (ClipboardState): The ClipboardState fixture instance.

    RETURNS (None): Raises an assertion if the data differs or the instance
        is not ClipboardState.
    """
    initial_data = {"key1": "value1", "key2": "value2"}
    clipboard_state.write(initial_data)

    copied_state = clipboard_state.deep_copy()

    assert isinstance(copied_state, ClipboardState)
    assert copied_state.read() == initial_data


@pytest.mark.unit
def test_classmethod_copy_and_paste():
    """
    Test the ClipboardState class methods clipboard_copy and clipboard_paste
    under mocked conditions.

    1. Patch the class methods to store clipboard data in an in-memory variable.
    2. Verify that copying a string sets the in-memory content.
    3. Verify that pasting returns the same string.

    RETURNS (None): Raises an assertion if the class methods do not behave
        as expected.
    """
    mock_clipboard_content = ""

    def mock_copy(text: str) -> None:
        nonlocal mock_clipboard_content
        mock_clipboard_content = text

    def mock_paste() -> str:
        return mock_clipboard_content

    with (
        patch.object(ClipboardState, "clipboard_copy", side_effect=mock_copy),
        patch.object(ClipboardState, "clipboard_paste", side_effect=mock_paste),
    ):
        test_string = "Hello, classmethod!"
        ClipboardState.clipboard_copy(test_string)
        assert mock_clipboard_content == test_string

        pasted_text = ClipboardState.clipboard_paste()
        assert pasted_text == test_string
