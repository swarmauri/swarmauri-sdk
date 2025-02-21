"""Unit tests for JupyterExecuteNotebookTool.

This module contains pytest-based unit tests that verify the functionality of
the JupyterExecuteNotebookTool class. The tests ensure that the tool correctly
executes Jupyter notebooks, handles errors, and returns the expected results.
"""

from unittest.mock import patch, MagicMock, mock_open
from nbclient.exceptions import CellExecutionError
from nbformat.notebooknode import NotebookNode

from swarmauri_tool_jupyterexecutenotebook.JupyterExecuteNotebookTool import (
    JupyterExecuteNotebookTool,
)
from swarmauri_base.tools.ToolBase import ToolBase


def test_inheritance() -> None:
    """
    Test that JupyterExecuteNotebookTool inherits from the base class ToolBase.
    """
    assert issubclass(
        JupyterExecuteNotebookTool, ToolBase
    ), "JupyterExecuteNotebookTool should inherit from ToolBase."


def test_default_attributes() -> None:
    """
    Test that JupyterExecuteNotebookTool has all expected default attributes.
    """
    tool = JupyterExecuteNotebookTool()
    assert tool.version == "1.0.0", "Expected default version to be 1.0.0."
    assert (
        tool.name == "JupyterExecuteNotebookTool"
    ), "Expected default name to be JupyterExecuteNotebookTool."
    assert (
        tool.type == "JupyterExecuteNotebookTool"
    ), "Expected tool type to be JupyterExecuteNotebookTool."
    assert (
        len(tool.parameters) == 2
    ), "Expected two default parameters (notebook_path, timeout)."


@patch("builtins.open", new_callable=mock_open, read_data="{}")
@patch("nbformat.read")
@patch(
    "swarmauri_tool_jupyterexecutenotebook.JupyterExecuteNotebookTool.NotebookClient"
)
def test_call_executes_notebook(
    mock_notebook_client: MagicMock, mock_nbformat_read: MagicMock, mock_file: MagicMock
) -> None:
    """
    Test that calling the tool with valid arguments executes the notebook
    and returns the updated NotebookNode.
    """
    mock_notebook = MagicMock(spec=NotebookNode)
    mock_nbformat_read.return_value = mock_notebook
    client_instance = MagicMock()
    mock_notebook_client.return_value = client_instance

    tool = JupyterExecuteNotebookTool()
    result = tool("fake_notebook.ipynb", timeout=60)

    mock_notebook_client.assert_called_once_with(
        mock_notebook, timeout=60, kernel_name="python3", allow_errors=True
    )
    client_instance.execute.assert_called_once()
    assert (
        result == mock_notebook
    ), "Expected the tool to return the executed NotebookNode."


@patch("builtins.open", new_callable=mock_open, read_data="{}")
@patch("nbformat.read")
@patch("nbclient.NotebookClient")
def test_call_cell_execution_error(
    mock_notebook_client: MagicMock, mock_nbformat_read: MagicMock, mock_file: MagicMock
) -> None:
    """
    Test that a CellExecutionError raised during notebook execution is logged
    and the partially executed notebook is returned.
    """
    mock_notebook = MagicMock(spec=NotebookNode)
    mock_nbformat_read.return_value = mock_notebook
    client_instance = MagicMock()
    mock_notebook_client.return_value = client_instance

    # Configure the client to raise CellExecutionError
    client_instance.execute.side_effect = CellExecutionError(
        "ErrorName", "ErrorValue", "Traceback"
    )

    tool = JupyterExecuteNotebookTool()
    result = tool("fake_notebook.ipynb")

    assert (
        result == mock_notebook
    ), "Even if a CellExecutionError occurs, the tool should return the notebook."


@patch("builtins.open", new_callable=mock_open, read_data="{}")
@patch("nbformat.read")
@patch("nbclient.NotebookClient")
def test_call_unexpected_exception(
    mock_notebook_client: MagicMock, mock_nbformat_read: MagicMock, mock_file: MagicMock
) -> None:
    """
    Test that an unexpected exception during notebook execution is logged
    and the notebook (possibly unmodified) is still returned.
    """
    mock_notebook = MagicMock(spec=NotebookNode)
    mock_nbformat_read.return_value = mock_notebook
    client_instance = MagicMock()
    mock_notebook_client.return_value = client_instance

    # Configure the client to raise a generic exception
    client_instance.execute.side_effect = ValueError("Unexpected error.")

    tool = JupyterExecuteNotebookTool()
    result = tool("fake_notebook.ipynb")

    assert (
        result == mock_notebook
    ), "When an unexpected exception occurs, the tool should still return the notebook."
