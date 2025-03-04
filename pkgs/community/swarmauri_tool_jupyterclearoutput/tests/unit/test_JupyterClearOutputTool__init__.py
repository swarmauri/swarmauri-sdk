"""
Unit tests for the swarmauri_tool_jupyterclearoutput package initialization.

This module uses pytest to verify that the package's __init__.py file
correctly exposes and imports required classes and variables.
It also ensures that the exposed objects behave as expected.
"""

from swarmauri_tool_jupyterclearoutput import JupyterClearOutputTool, __version__


class BaseTest:
    """
    Base class for all test classes in this module.
    This can be extended to include shared setup or teardown logic for tests.
    """


class TestSwarmAuriToolsInit(BaseTest):
    """
    Test suite for swarmauri_tool_jupyterclearoutput package initialization.
    Ensures the correctness of imports and exposed objects within __init__.py.
    """

    def test_jupyter_clear_output_tool_import(self) -> None:
        """
        Test if JupyterClearOutputTool is imported correctly and can be instantiated.
        """
        tool_instance = JupyterClearOutputTool()
        assert tool_instance is not None, "JupyterClearOutputTool instantiation failed."

    def test_version_availability(self) -> None:
        """
        Test if __version__ is defined and is a non-empty string.
        """
        assert __version__ is not None, "Expected __version__ to be defined."
        assert isinstance(__version__, str), "Expected __version__ to be a string."
        assert __version__ != "", "Expected __version__ to be a non-empty string."
