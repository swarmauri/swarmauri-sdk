"""
test_JupyterReadNotebookTool.py

This module contains pytest-based unit tests for the JupyterReadNotebookTool class.
It verifies the functionality of reading and validating Jupyter notebooks, as well
as handling various error conditions.
"""

import pytest
from unittest.mock import patch, MagicMock
from nbformat.validator import NotebookValidationError
from swarmauri_tool_jupyterreadnotebook.JupyterReadNotebookTool import (
    JupyterReadNotebookTool,
)


def fake_nb_validation(*args, **kwargs):
    """
    Helper function to simulate a notebook validation error by raising
    NotebookValidationError with a dummy exception object that has the
    required attributes: 'message', 'instance', 'validator', 'relative_schema_path',
    and 'relative_path'.
    """
    from types import SimpleNamespace

    dummy = SimpleNamespace(
        message="Notebook is invalid",
        instance="dummy instance",
        validator="dummy validator",
        relative_schema_path=[],  # Required for formatting the error
        relative_path=[],         # Added to satisfy the expected attribute
    )
    raise NotebookValidationError(dummy)


@pytest.fixture
def jupyter_read_notebook_tool() -> JupyterReadNotebookTool:
    """
    A pytest fixture that returns an instance of JupyterReadNotebookTool for use in tests.
    """
    return JupyterReadNotebookTool()


def test_tool_initialization(
    jupyter_read_notebook_tool: JupyterReadNotebookTool,
) -> None:
    """
    Test that the tool initializes correctly with the expected default values.
    """
    assert jupyter_read_notebook_tool.version == "1.0.0"
    assert len(jupyter_read_notebook_tool.parameters) == 2
    assert jupyter_read_notebook_tool.name == "JupyterReadNotebookTool"
    assert jupyter_read_notebook_tool.description.startswith("Reads a Jupyter notebook")
    assert jupyter_read_notebook_tool.type == "JupyterReadNotebookTool"


@patch("nbformat.read")
@patch("nbformat.validate")
def test_call_success(
    mock_validate: MagicMock,
    mock_read: MagicMock,
    jupyter_read_notebook_tool: JupyterReadNotebookTool,
) -> None:
    """
    Test successful reading and validating of a Jupyter notebook.
    """
    # Arrange
    mock_notebook_node = {"cells": [], "metadata": {}}
    mock_read.return_value = mock_notebook_node

    # Act
    result = jupyter_read_notebook_tool("dummy_path", as_version=4)

    # Assert
    mock_read.assert_called_once_with("dummy_path", as_version=4)
    mock_validate.assert_called_once_with(mock_notebook_node)
    assert "notebook_node" in result
    assert result["notebook_node"] == mock_notebook_node


@patch("nbformat.read", side_effect=FileNotFoundError)
def test_call_file_not_found(
    mock_read: MagicMock, jupyter_read_notebook_tool: JupyterReadNotebookTool
) -> None:
    """
    Test handling of the FileNotFoundError when the notebook file is absent.
    """
    result = jupyter_read_notebook_tool("non_existent_path.ipynb", as_version=4)
    assert "error" in result
    assert "File not found" in result["error"]
    mock_read.assert_called_once()


@patch("nbformat.read", return_value={"cells": [], "metadata": {}})
@patch("nbformat.validate", side_effect=fake_nb_validation)
def test_call_validation_error(
    mock_validate: MagicMock,
    mock_read: MagicMock,
    jupyter_read_notebook_tool: JupyterReadNotebookTool,
) -> None:
    """
    Test handling of a NotebookValidationError when the notebook structure is invalid.
    """
    result = jupyter_read_notebook_tool("invalid_notebook.ipynb", as_version=4)
    assert "error" in result
    assert "Notebook validation error" in result["error"]
    mock_read.assert_called_once()
    mock_validate.assert_called_once()


@patch("nbformat.read", side_effect=Exception("Unexpected error"))
def test_call_unexpected_exception(
    mock_read: MagicMock, jupyter_read_notebook_tool: JupyterReadNotebookTool
) -> None:
    """
    Test that an unexpected exception is handled gracefully with an appropriate error message.
    """
    result = jupyter_read_notebook_tool("any_path.ipynb", as_version=4)
    assert "error" in result
    assert "Failed to read notebook" in result["error"]
    mock_read.assert_called_once()


@patch("nbformat.read")
@patch("nbformat.validate")
def test_call_non_empty_read(
    mock_validate: MagicMock,
    mock_read: MagicMock,
    jupyter_read_notebook_tool: JupyterReadNotebookTool,
) -> None:
    """
    Test reading and validating a non-empty Jupyter notebook.
    """
    # Arrange: Create a non-empty notebook node
    non_empty_notebook = {
        "cells": [
            {
                "cell_type": "code",
                "execution_count": 1,
                "metadata": {},
                "outputs": [],
                "source": "print('Hello, world!')"
            }
        ],
        "metadata": {"language_info": {"name": "python"}}
    }
    mock_read.return_value = non_empty_notebook

    # Act
    result = jupyter_read_notebook_tool("non_empty_notebook.ipynb", as_version=4)

    # Assert
    mock_read.assert_called_once_with("non_empty_notebook.ipynb", as_version=4)
    mock_validate.assert_called_once_with(non_empty_notebook)
    assert "notebook_node" in result
    assert result["notebook_node"] == non_empty_notebook
    # Ensure the notebook contains at least one cell
    assert len(result["notebook_node"]["cells"]) > 0
