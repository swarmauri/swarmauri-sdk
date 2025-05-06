"""
Module: test___init__.py

This module contains pytest-based unit tests for the __init__.py file of the
swarmauri_tool_jupytergetshellmessage package. It ensures that the package
is correctly exporting classes and attributes, including the JupyterGetShellMessageTool
class and the package version.
"""

from typing import Any


# Import from the package's __init__.py file
from swarmauri_tool_jupytergetshellmessage import (
    JupyterGetShellMessageTool,
    __version__,
    __all__,
)


class BaseTestCase:
    """
    A simple base class for test cases. In a more complex test suite, this
    class could house shared setup logic, tear-down routines, or common
    utility methods needed by all test classes.
    """

    def common_setup(self) -> None:
        """
        Common setup method for all test classes inheriting from BaseTestCase.
        """
        pass


class TestInit(BaseTestCase):
    """
    TestInit is responsible for validating the exports from the
    package's __init__.py file. It ensures that core components
    like JupyterGetShellMessageTool are accessible and functional.
    """

    def test_jupyter_get_shell_message_tool_in_all(self) -> None:
        """
        Verify that the JupyterGetShellMessageTool class is listed in __all__.
        This ensures that it is exposed as part of the package's public API.
        """
        self.common_setup()
        assert "JupyterGetShellMessageTool" in __all__, (
            "JupyterGetShellMessageTool should be in __all__"
        )

    def test_can_instantiate_jupyter_get_shell_message_tool(self) -> None:
        """
        Check that a JupyterGetShellMessageTool instance can be created
        without raising any exceptions.
        """
        self.common_setup()
        tool_instance: Any = JupyterGetShellMessageTool()
        assert tool_instance is not None, (
            "Failed to instantiate JupyterGetShellMessageTool."
        )

    def test_version_is_string(self) -> None:
        """
        Confirm that __version__ is defined as a string, indicating
        the package version is correctly set.
        """
        self.common_setup()
        assert isinstance(__version__, str), "__version__ should be a string."

    def test_version_is_not_empty(self) -> None:
        """
        Check that the version string is not empty. This test ensures that
        the package version has been properly assigned.
        """
        self.common_setup()
        assert __version__ != "", "__version__ should not be empty."
