"""
Unit tests for the swarmauri_tool_jupyterfromdict package initialization.

This module uses pytest to verify that the package's __init__.py
correctly exposes the expected classes and variables, including the
JupyterFromDictTool class and the __version__ string.

All tests in this file ensure that:
  - JupyterFromDictTool is importable
  - An instance of JupyterFromDictTool can be created (if constructor allows)
  - __version__ is a valid string
"""

import pytest
from swarmauri_tool_jupyterfromdict import JupyterFromDictTool, __version__
from swarmauri_tool_jupyterfromdict import __all__


class TestInit:
    """Test cases for the swarmauri_tool_jupyterfromdict package initialization."""

    def test_jupyter_from_dict_tool_in_all(self) -> None:
        """
        Verify that JupyterFromDictTool is listed in __all__,
        indicating it is exposed by the package's __init__.py.
        """
        assert "JupyterFromDictTool" in __all__, (
            "JupyterFromDictTool should be included in __all__ but is missing."
        )

    def test_jupyter_from_dict_tool_import(self) -> None:
        """
        Verify that JupyterFromDictTool is importable from the package
        and is not None.
        """
        assert JupyterFromDictTool is not None, (
            "JupyterFromDictTool should be importable and not None."
        )

    def test_jupyter_from_dict_tool_instantiation(self) -> None:
        """
        Check that an instance of JupyterFromDictTool can be created.
        Adjust instantiation parameters if the class requires any arguments.
        """
        tool_instance = JupyterFromDictTool()
        assert tool_instance is not None, (
            "An instance of JupyterFromDictTool should be successfully created."
        )

    def test_package_version_is_string(self) -> None:
        """
        Ensure that __version__ is a valid non-empty string.
        """
        assert isinstance(__version__, str), (
            "__version__ should be a string."
        )
        assert __version__, (
            "__version__ should not be an empty string."
        )