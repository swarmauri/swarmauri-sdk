"""
Module containing unit tests for the swarmauri_tool_jupyterdisplay package initialization.

The tests in this file ensure that all modules, classes, and attributes are correctly
exposed at the package level, including verifying the presence of JupyterDisplayTool and
the package's version string.
"""

import pytest
from swarmauri_tool_jupyterdisplay import JupyterDisplayTool, __version__


class TestPackageInit:
    """Test suite for the swarmauri_tool_jupyterdisplay package initialization."""

    def test_jupyter_display_tool_exposed(self) -> None:
        """
        Test that JupyterDisplayTool is exposed at the package level.
        """
        assert JupyterDisplayTool is not None, (
            "Expected JupyterDisplayTool to be exposed by the package."
        )

    def test_package_version_exposed(self) -> None:
        """
        Test that the package version is available in __version__.
        """
        # Check that __version__ is a non-empty string
        assert isinstance(__version__, str) and len(__version__) > 0, (
            "Expected a non-empty string for __version__."
        )