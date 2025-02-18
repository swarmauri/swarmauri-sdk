"""
Unit tests for verifying the package initialization of swarmauri_tool_jupyterexportlatex.

This module ensures the __init__.py file correctly exposes the JupyterExportLatexTool class
and the __version__ attribute, validating the package setup and exports.
"""

from typing import Any
import pytest
from swarmauri_tool_jupyterexportlatex import JupyterExportLatexTool, __version__


def test_jupyter_export_latex_tool_imported_properly() -> None:
    """
    Test that JupyterExportLatexTool can be imported and instantiated without errors.

    Verifies that the class is exposed properly through the package's __init__.py.
    """
    tool: Any = JupyterExportLatexTool()
    assert tool is not None, "JupyterExportLatexTool was not properly instantiated."


def test_package_version_is_exposed() -> None:
    """
    Test that the __version__ attribute is exposed and is a non-empty string.

    Validates the package's versioning information as part of initialization.
    """
    assert isinstance(__version__, str), "__version__ should be a string."
    assert __version__, "__version__ should not be empty."