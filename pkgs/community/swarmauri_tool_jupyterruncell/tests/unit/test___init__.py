"""
This module contains pytest-based unit tests for the swarmauri_tool_jupyterruncell package's __init__.py file.
It ensures that the package initialization is correct and that exposed classes and variables behave as expected.
"""

import pytest
from swarmauri_tool_jupyterruncell import JupyterRunCellTool, __version__


def test_jupyter_run_cell_tool_import() -> None:
    """
    Test that the JupyterRunCellTool class is imported from the package's __init__.py.
    Ensures that the class is accessible after the package is initialized.
    """
    assert JupyterRunCellTool is not None, "JupyterRunCellTool should be exposed by __init__.py"


def test_jupyter_run_cell_tool_instantiation() -> None:
    """
    Test that the JupyterRunCellTool class can be instantiated without errors.
    Ensures that the constructor functions correctly.
    """
    instance = JupyterRunCellTool()
    assert isinstance(instance, JupyterRunCellTool), (
        "Instance should be of type JupyterRunCellTool"
    )


def test_package_version_is_defined() -> None:
    """
    Test that the package's __version__ attribute is defined.
    Ensures that the version is accessible after initialization.
    """
    assert __version__ is not None, "__version__ should be defined in __init__.py"
    assert isinstance(__version__, str), "__version__ should be a string"
    # If needed, further checks on version string format could be added here.