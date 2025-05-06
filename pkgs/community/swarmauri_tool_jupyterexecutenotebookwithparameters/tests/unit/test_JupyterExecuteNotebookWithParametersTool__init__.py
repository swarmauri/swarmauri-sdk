"""
Unit tests for the package's initialization. Ensures that the __init__ module
correctly exposes the JupyterExecuteNotebookWithParametersTool class and version.
"""

from typing import Any

from swarmauri_tool_jupyterexecutenotebookwithparameters import (
    JupyterExecuteNotebookWithParametersTool,
    __version__,
)


def test_jupyter_execute_notebook_with_parameters_tool_import() -> None:
    """
    Test that the JupyterExecuteNotebookWithParametersTool is successfully
    imported from the package's __init__.py file.
    """
    tool_instance: Any = JupyterExecuteNotebookWithParametersTool()
    assert isinstance(tool_instance, JupyterExecuteNotebookWithParametersTool), (
        "JupyterExecuteNotebookWithParametersTool should be an instance of the specified class"
    )


def test_package_version_exists() -> None:
    """
    Test that the __version__ attribute is defined in the package's __init__.py.
    """
    assert __version__ is not None, "The package should define a __version__ attribute"
    assert isinstance(__version__, str), "The package's __version__ should be a string"
