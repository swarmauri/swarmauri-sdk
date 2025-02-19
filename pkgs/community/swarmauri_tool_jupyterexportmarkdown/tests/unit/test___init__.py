"""
Unit tests for the swarmauri_tool_jupyterexportmarkdown package initialization.

This module ensures that the __init__.py file correctly exposes the JupyterExportMarkdownTool
class and the __version__ attribute.
"""

from swarmauri_tool_jupyterexportmarkdown import (
    JupyterExportMarkdownTool,
    __version__,
)


def test_jupyter_export_markdown_tool_existence() -> None:
    """
    Test that the JupyterExportMarkdownTool class is properly exposed by the package.
    Verifies that the imported symbol is not None and is indeed a class.
    """
    assert JupyterExportMarkdownTool is not None, (
        "JupyterExportMarkdownTool should be exposed by "
        "swarmauri_tool_jupyterexportmarkdown.__init__.py"
    )
    assert isinstance(JupyterExportMarkdownTool, type), (
        "JupyterExportMarkdownTool should be a class."
    )


def test_package_version_is_string() -> None:
    """
    Test the __version__ attribute to confirm it is a string.
    """
    assert isinstance(__version__, str), (
        "__version__ should be set and must be a string."
    )
