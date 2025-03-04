import pyperclip
from typing import Dict, Any
from swarmauri.state.base.StateBase import StateBase


class ClipboardState(StateBase):
    """
    A concrete implementation of StateBase that uses the system clipboard to store and retrieve state data.
    """

    def read(self) -> Dict[str, Any]:
        """
        Reads the current state from the clipboard as a dictionary.
        """
        try:
            clipboard_content = pyperclip.paste()
            # Ensure the clipboard contains valid data (e.g., a JSON string that can be parsed)
            if clipboard_content:
                return eval(
                    clipboard_content
                )  # Replace eval with JSON for safer parsing
            return {}
        except Exception as e:
            raise ValueError(f"Failed to read state from clipboard: {e}")

    def write(self, data: Dict[str, Any]) -> None:
        """
        Replaces the current state with the given data by copying it to the clipboard.
        """
        try:
            pyperclip.copy(
                str(data)
            )  # Convert dictionary to string for clipboard storage
        except Exception as e:
            raise ValueError(f"Failed to write state to clipboard: {e}")

    def update(self, data: Dict[str, Any]) -> None:
        """
        Updates the current state with the given data by merging with clipboard content.
        """
        try:
            current_state = self.read()
            current_state.update(data)
            self.write(current_state)
        except Exception as e:
            raise ValueError(f"Failed to update state on clipboard: {e}")

    def reset(self) -> None:
        """
        Resets the clipboard state to an empty dictionary.
        """
        try:
            self.write({})
        except Exception as e:
            raise ValueError(f"Failed to reset clipboard state: {e}")

    def deep_copy(self) -> "ClipboardState":
        """
        Creates a deep copy of the current state. In this context, simply returns a new ClipboardState with the same clipboard data.
        """
        try:
            current_state = self.read()
            new_instance = ClipboardState()
            new_instance.write(current_state)
            return new_instance
        except Exception as e:
            raise ValueError(
                f"Failed to create a deep copy of the clipboard state: {e}"
            )
