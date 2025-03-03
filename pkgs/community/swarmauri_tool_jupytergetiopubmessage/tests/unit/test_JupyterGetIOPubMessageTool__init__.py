"""Unit tests for the package initialization of swarmauri_tool_jupytergetiopubmessage.

This module ensures that __init__.py exposes the JupyterGetIOPubMessageTool class and
that the package version is defined as expected.
"""

from typing import Callable

from swarmauri_tool_jupytergetiopubmessage import (
    __version__,
    JupyterGetIOPubMessageTool,
)


class BaseTest:
    """A base test class providing common setup and teardown functionality."""

    def setup_method(self, method: Callable) -> None:
        """
        Perform setup before each test method.

        :param method: The test method for which the setup is being performed.
        """
        # Setup logic (if needed) goes here
        pass

    def teardown_method(self, method: Callable) -> None:
        """
        Perform teardown after each test method.

        :param method: The test method for which the teardown is being performed.
        """
        # Teardown logic (if needed) goes here
        pass


class TestInit(BaseTest):
    """Test suite for verifying the swarmauri_tool_jupytergetiopubmessage package initialization."""

    def test_jupyter_get_iopub_message_tool_existence(self) -> None:
        """
        Test that the JupyterGetIOPubMessageTool class is correctly imported from __init__.py.
        """
        tool_instance = JupyterGetIOPubMessageTool()
        assert tool_instance is not None, (
            "Failed to create an instance of JupyterGetIOPubMessageTool."
        )

    def test_version_defined(self) -> None:
        """
        Test that the package version is defined and is not an empty string.
        """
        assert __version__, "Package __version__ is missing or empty."
        assert isinstance(__version__, str), "__version__ should be a string."
