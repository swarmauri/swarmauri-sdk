"""
Unit tests for the swarmauri_tool_jupyterwritenotebook package initialization.

This module tests that the package's __init__.py file correctly exposes its
public API and provides necessary metadata such as version information.
"""

import pytest
from swarmauri_tool_jupyterwritenotebook import JupyterWriteNotebookTool, __version__


def test_jupyter_write_notebook_tool_import() -> None:
    """
    Test that JupyterWriteNotebookTool can be imported from the package.
    Ensures that the class is properly exposed in __init__.py.
    """
    assert JupyterWriteNotebookTool is not None, "Expected JupyterWriteNotebookTool to be exposed."


def test_jupyter_write_notebook_tool_instantiation() -> None:
    """
    Verify that the JupyterWriteNotebookTool can be instantiated
    without errors.
    """
    tool_instance = JupyterWriteNotebookTool()
    assert isinstance(tool_instance, JupyterWriteNotebookTool), (
        "Expected tool_instance to be an instance of JupyterWriteNotebookTool."
    )


def test_package_version_existence() -> None:
    """
    Check that the __version__ attribute exists and has the correct format.
    """
    assert __version__, "Expected __version__ to be defined in package."
    assert isinstance(__version__, str), "Expected __version__ to be a string."
    # A simple check that version string has at least a major version
    assert len(__version__) > 0, "Expected a non-empty version string."