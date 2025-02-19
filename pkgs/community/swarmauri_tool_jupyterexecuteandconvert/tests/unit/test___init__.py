"""
Unit tests for the swarmauri_tool_jupyterexecuteandconvert package's __init__ module.

This module tests that the package's initialization logic functions as expected.
Specifically, it ensures that JupyterExecuteAndConvertTool is correctly exposed
and that the package version attribute is accessible.
"""

from swarmauri_tool_jupyterexecuteandconvert import (
    JupyterExecuteAndConvertTool,
    __version__,
)


def test_jupyter_execute_and_convert_tool_exposed() -> None:
    """
    Test that the JupyterExecuteAndConvertTool is exposed via the package's __init__.
    """
    # Create an instance of JupyterExecuteAndConvertTool to verify it's imported correctly.
    instance = JupyterExecuteAndConvertTool()
    assert instance is not None, (
        "Expected a valid instance of JupyterExecuteAndConvertTool."
    )


def test_package_version_available() -> None:
    """
    Test that the package version is properly exposed as a string. The version may be '0.0.0'
    if the package is not installed (e.g., during development), but it should still be defined.
    """
    # Check that __version__ is defined and is a string.
    assert isinstance(__version__, str), "Expected __version__ to be a string."
