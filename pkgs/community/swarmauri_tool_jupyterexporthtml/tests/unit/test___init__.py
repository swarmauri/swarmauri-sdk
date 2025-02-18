"""
Module containing pytest tests for the package initialization.

This module tests that the swarmauri_tool_jupyterexporthtml package
exposes the necessary components through its __init__.py.
"""

import pytest
from swarmauri_tool_jupyterexporthtml import JupyterExportHTMLTool, __version__


class TestPackageInit:
    """
    A test suite for ensuring the package initialization works as expected.
    """

    def test_jupyter_export_html_tool_import(self) -> None:
        """
        Test that the JupyterExportHTMLTool can be imported from the package.

        This test ensures that we're able to import the JupyterExportHTMLTool
        class from the main package __init__.py, verifying that it is correctly
        exposed by the package initialization.
        """
        assert JupyterExportHTMLTool is not None, (
            "JupyterExportHTMLTool should be defined and imported from the "
            "swarmauri_tool_jupyterexporthtml package."
        )

    def test_package_version_import(self) -> None:
        """
        Test that the __version__ attribute is available in the package.

        This test verifies that the __version__ attribute is correctly
        imported and is a non-empty string.
        """
        assert isinstance(__version__, str), "Package __version__ should be a string."
        assert __version__, "Package __version__ should not be empty."