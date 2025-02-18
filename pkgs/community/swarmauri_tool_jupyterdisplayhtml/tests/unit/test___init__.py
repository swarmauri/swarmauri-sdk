"""
Module-level docstring:
This module provides pytest-based test cases for verifying that the package
swarmauri_tool_jupyterdisplayhtml initializes correctly and that the members
from __init__.py are exposed as expected.
"""

import pytest
from swarmauri_tool_jupyterdisplayhtml import __version__, __all__, JupyterDisplayHTMLTool


class TestInit(object):
    """
    Test class for verifying the initialization behavior of the
    swarmauri_tool_jupyterdisplayhtml package.
    """

    def test_jupyterdisplayhtmltool_in_all(self) -> None:
        """
        Ensures 'JupyterDisplayHTMLTool' is exposed in the package's __all__ list.

        This test checks if the package initialization correctly includes
        JupyterDisplayHTMLTool in the __all__ attribute.
        """
        assert "JupyterDisplayHTMLTool" in __all__, (
            "Expected 'JupyterDisplayHTMLTool' to be in __all__, but it was not found."
        )

    def test_version_is_string(self) -> None:
        """
        Ensures that __version__ is exposed and is a string.

        This test checks that the __version__ attribute is not None and
        that it is of type string.
        """
        assert __version__ is not None, (
            "Expected '__version__' to be defined, but it is None."
        )
        assert isinstance(__version__, str), (
            f"Expected '__version__' to be a str, got {type(__version__)}."
        )

    def test_jupyterdisplayhtmltool_instantiation(self) -> None:
        """
        Verifies that an instance of JupyterDisplayHTMLTool can be created.

        This test checks that the constructor for JupyterDisplayHTMLTool does
        not raise an exception, ensuring the tool is validly exposed.
        """
        tool = None
        try:
            tool = JupyterDisplayHTMLTool()
        except Exception as exc:
            pytest.fail(f"Instantiating JupyterDisplayHTMLTool raised an exception: {exc}")
        assert tool is not None, (
            "Failed to instantiate JupyterDisplayHTMLTool."
        )