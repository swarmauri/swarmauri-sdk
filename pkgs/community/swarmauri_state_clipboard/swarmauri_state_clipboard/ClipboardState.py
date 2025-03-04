"""
This module provides a ClipboardState class that implements a system clipboard-based approach
to storing and retrieving state data. It uses only built-in Python modules and platform-specific
commands (clip on Windows, pbcopy/pbpaste on macOS, xclip on Linux).
"""

import subprocess
import sys
from typing import Dict, Literal

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.state.StateBase import StateBase


@ComponentBase.register_type(StateBase, "ClipboardState")
class ClipboardState(StateBase):
    """A concrete implementation of StateBase that uses the system clipboard
    to store and retrieve state data.

    The class relies on the standard library for subprocess calls to external
    commands available on each platform. If these commands are missing, a
    FileNotFoundError or subprocess.CalledProcessError may be raised.
    """

    type: Literal["ClipboardState"] = "ClipboardState"

    @classmethod
    def clipboard_paste(cls, text: str) -> None:
        """Copy the given text to the system clipboard using standard library calls.

        text (str): The text to copy to the clipboard.
        RETURNS (None): This method does not return anything.
        RAISES (FileNotFoundError, subprocess.CalledProcessError):
            If the underlying system command is unavailable or fails.
        """
        platform = sys.platform
        if platform.startswith("win"):
            # Windows: uses 'clip' command
            with subprocess.Popen(["clip"], stdin=subprocess.PIPE, text=True) as proc:
                proc.communicate(text)
        elif platform.startswith("darwin"):
            # macOS: uses 'pbcopy'
            with subprocess.Popen(["pbcopy"], stdin=subprocess.PIPE, text=True) as proc:
                proc.communicate(text)
        else:
            # Linux/Unix: uses 'xclip'
            with subprocess.Popen(
                ["xclip", "-selection", "clipboard"], stdin=subprocess.PIPE, text=True
            ) as proc:
                proc.communicate(text)

    @classmethod
    def clipboard_copy(cls) -> str:
        """Retrieve text from the system clipboard using standard library calls.

        RETURNS (str): The text contents of the system clipboard.
        RAISES (FileNotFoundError, subprocess.CalledProcessError):
            If the underlying system command is unavailable or fails.
        """
        platform = sys.platform
        if platform.startswith("win"):
            # Windows: No direct paste command, so we use PowerShell
            completed = subprocess.run(
                ["powershell", "-command", "Get-Clipboard"],
                capture_output=True,
                text=True,
            )
            return completed.stdout
        elif platform.startswith("darwin"):
            # macOS: uses 'pbpaste'
            completed = subprocess.run(["pbpaste"], capture_output=True, text=True)
            return completed.stdout
        else:
            # Linux/Unix: uses 'xclip'
            completed = subprocess.run(
                ["xclip", "-selection", "clipboard", "-o"],
                capture_output=True,
                text=True,
            )
            return completed.stdout

    def read(self) -> Dict[str, str]:
        """Read the current state from the system clipboard as a dictionary.

        RETURNS (Dict[str, str]): The clipboard data parsed as a dictionary.
            Returns an empty dictionary if clipboard content is empty.
        RAISES (ValueError): If there is an error reading or parsing the state.
        """
        try:
            # Use the class method via the class
            clipboard_content = self.__class__.clipboard_copy()

            # For safety, replace eval with safer alternatives
            if clipboard_content.strip():
                import ast

                # Use ast.literal_eval which is much safer than eval()
                # It only evaluates literals, not arbitrary code
                return ast.literal_eval(clipboard_content)
            return {}
        except Exception as e:
            raise ValueError(f"Failed to read state from clipboard: {e}")

    def write(self, data: Dict[str, str]) -> None:
        """Replace the current state with the given data by copying it to the clipboard.

        data (Dict[str, str]): The state data to write.
        RETURNS (None): This method does not return anything.
        RAISES (ValueError): If there is an error writing to the clipboard.
        """
        if isinstance(data, str):
            raise ValueError("Must be data must be type Dict.")
        try:
            self.__class__.clipboard_paste(str(data))
        except Exception as e:
            raise ValueError(f"Failed to write state to clipboard: {e}")

    def update(self, data: Dict[str, str]) -> None:
        """Update the current clipboard state by merging existing state with new data.

        data (Dict[str, str]): The new state data to merge into the existing clipboard state.
        RETURNS (None): This method does not return anything.
        RAISES (ValueError): If there is an error updating the clipboard state.
        """
        try:
            current_state = self.read()
            current_state.update(data)
            self.write(current_state)
        except Exception as e:
            raise ValueError(f"Failed to update state on clipboard: {e}")

    def reset(self) -> None:
        """Reset the clipboard state to an empty dictionary.

        RETURNS (None): This method does not return anything.
        RAISES (ValueError): If there is an error resetting the clipboard state.
        """
        try:
            self.write({})
        except Exception as e:
            raise ValueError(f"Failed to reset clipboard state: {e}")

    def deep_copy(self) -> "ClipboardState":
        """Create a deep copy of the current state as a new ClipboardState instance.

        RETURNS (ClipboardState): A new ClipboardState instance with the same clipboard data.
        RAISES (ValueError): If there is an error creating the deep copy of the state.
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
