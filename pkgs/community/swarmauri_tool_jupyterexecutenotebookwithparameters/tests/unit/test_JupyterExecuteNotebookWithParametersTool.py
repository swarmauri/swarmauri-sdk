"""
test_JupyterExecuteNotebookWithParametersTool.py

This module contains the pytest test cases for the JupyterExecuteNotebookWithParametersTool class.
It verifies that the tool behaves correctly, including attribute checks, parameter handling,
file path validations, and error handling during notebook execution.
"""

import pytest
from unittest.mock import patch, MagicMock
from swarmauri_tool_jupyterexecutenotebookwithparameters.JupyterExecuteNotebookWithParametersTool import (
    JupyterExecuteNotebookWithParametersTool,
)


@pytest.fixture
def tool_instance() -> JupyterExecuteNotebookWithParametersTool:
    """
    Provides an instance of the JupyterExecuteNotebookWithParametersTool for testing.
    """
    return JupyterExecuteNotebookWithParametersTool()


def test_class_attributes(
    tool_instance: JupyterExecuteNotebookWithParametersTool,
) -> None:
    """
    Test that the class attributes match expected default values.
    """
    assert tool_instance.version == "1.0.0"
    assert tool_instance.name == "JupyterExecuteNotebookWithParametersTool"
    assert tool_instance.type == "JupyterExecuteNotebookWithParametersTool"
    assert len(tool_instance.parameters) == 3


def test_call_incorrect_notebook_extension(
    tool_instance: JupyterExecuteNotebookWithParametersTool,
) -> None:
    """
    Test that calling the tool with a non-ipynb notebook_path returns an error.
    """
    result = tool_instance(
        notebook_path="invalid_file.txt", output_notebook_path="out.ipynb"
    )
    assert "error" in result
    assert "not a .ipynb file" in result["error"]


def test_call_incorrect_output_extension(
    tool_instance: JupyterExecuteNotebookWithParametersTool,
) -> None:
    """
    Test that calling the tool with a non-ipynb output_notebook_path returns an error.
    """
    result = tool_instance(
        notebook_path="notebook.ipynb", output_notebook_path="out.txt"
    )
    assert "error" in result
    assert "not a .ipynb file" in result["error"]


@patch(
    "swarmauri_tool_jupyterexecutenotebookwithparameters.JupyterExecuteNotebookWithParametersTool.pm.execute_notebook"
)
def test_call_execution_success(
    mock_execute_notebook: MagicMock,
    tool_instance: JupyterExecuteNotebookWithParametersTool,
) -> None:
    """
    Test that calling the tool with valid paths calls papermill.execute_notebook
    and returns the path to the executed notebook.
    """
    mock_execute_notebook.return_value = None  # Simulate successful execution
    result = tool_instance(
        notebook_path="notebook.ipynb",
        output_notebook_path="executed_notebook.ipynb",
        params={"key": "value"},
    )
    assert "executed_notebook" in result
    assert result["executed_notebook"] == "executed_notebook.ipynb"
    mock_execute_notebook.assert_called_once_with(
        input_path="notebook.ipynb",
        output_path="executed_notebook.ipynb",
        parameters={"key": "value"},
    )


@patch(
    "swarmauri_tool_jupyterexecutenotebookwithparameters.JupyterExecuteNotebookWithParametersTool.pm.execute_notebook"
)
def test_call_execution_failure(
    mock_execute_notebook: MagicMock,
    tool_instance: JupyterExecuteNotebookWithParametersTool,
) -> None:
    """
    Test that an exception raised during papermill.execute_notebook is handled and
    returns an 'error' in the result dictionary.
    """
    mock_execute_notebook.side_effect = Exception("Simulated execution error")
    result = tool_instance(
        notebook_path="notebook.ipynb",
        output_notebook_path="executed_notebook.ipynb",
        params={"key": "value"},
    )
    assert "error" in result
    assert "Simulated execution error" in result["error"]
    mock_execute_notebook.assert_called_once()
