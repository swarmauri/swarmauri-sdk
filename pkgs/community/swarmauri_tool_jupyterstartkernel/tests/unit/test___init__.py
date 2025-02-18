#!/usr/bin/env python
# test___init__.py
"""
Unit tests for the swarmauri_tool_jupyterstartkernel package __init__.py file.

This module provides pytest-based test cases to ensure that the package
initialization logic is correct and the main components are properly exposed.
"""

from typing import Any


def test_jupyter_start_kernel_tool_is_importable() -> None:
    """
    Test that JupyterStartKernelTool is importable from the package's main module.
    This ensures that the __init__.py file properly exposes the class.
    """
    # Import the class from the root of the package to confirm exposure in __init__.py
    from swarmauri_tool_jupyterstartkernel import JupyterStartKernelTool
    assert JupyterStartKernelTool is not None, "JupyterStartKernelTool could not be imported."


def test_jupyter_start_kernel_tool_in_all() -> None:
    """
    Test that JupyterStartKernelTool is included in the package's __all__ list.
    This verifies that the class is declared in __all__.
    """
    from swarmauri_tool_jupyterstartkernel import __all__ as exposed
    assert "JupyterStartKernelTool" in exposed, "'JupyterStartKernelTool' not found in __all__."


def test_version_exists_and_is_string() -> None:
    """
    Test that the __version__ attribute is defined and is a string.
    This confirms that the package version is exposed correctly.
    """
    from swarmauri_tool_jupyterstartkernel import __version__
    assert __version__ is not None, "__version__ is not defined."
    assert isinstance(__version__, str), f"__version__ should be a string, got {type(__version__)}."