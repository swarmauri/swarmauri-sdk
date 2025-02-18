"""
test_JupyterExportPythonTool.py

This module contains pytest-based unit tests for the JupyterExportPythonTool class. It verifies
the functionality and correctness of the class defined in JupyterExportPythonTool.py, ensuring
it can successfully convert a Jupyter Notebook to a Python script or handle errors appropriately.
"""

import pytest
from unittest.mock import patch, MagicMock
from nbformat import NotebookNode

from swarmauri_tool_jupyterexportpython.JupyterExportPythonTool import JupyterExportPythonTool


@pytest.fixture
def mock_notebook() -> NotebookNode:
    """
    Provides a mock NotebookNode instance for testing.
    """
    nb = NotebookNode()
    nb["cells"] = []
    nb["metadata"] = {}
    return nb


def test_tool_initialization() -> None:
    """
    Tests that the JupyterExportPythonTool initializes with the expected attributes.
    """
    tool = JupyterExportPythonTool()
    assert tool.version == "1.0.0", "Expected default version to be 1.0.0"
    assert tool.name == "JupyterExportPythonTool", "Expected name to match class definition"
    assert tool.description == "Converts Jupyter Notebooks to Python scripts.", (
        "Tool description should match the declared string."
    )
    assert tool.type == "JupyterExportPythonTool", "Type should be 'JupyterExportPythonTool'"
    assert len(tool.parameters) == 2, "Expected exactly two default parameters"


@patch("swarmauri_tool_jupyterexportpython.JupyterExportPythonTool.PythonExporter")
def test_export_notebook_success(
    mock_exporter_class: MagicMock, mock_notebook: NotebookNode
) -> None:
    """
    Tests that the tool successfully exports a notebook to a Python script when the exporter
    runs without errors.
    """
    mock_exporter = mock_exporter_class.return_value
    mock_exporter.from_notebook_node.return_value = ("# Exported Python Script", None)

    tool = JupyterExportPythonTool()
    result = tool(notebook=mock_notebook)

    assert "exported_script" in result, "Expected 'exported_script' key in the result"
    assert "# Exported Python Script" in result["exported_script"], (
        "Exported script content should match the mock response."
    )


@patch("swarmauri_tool_jupyterexportpython.JupyterExportPythonTool.PythonExporter")
def test_export_notebook_with_template(
    mock_exporter_class: MagicMock, mock_notebook: NotebookNode
) -> None:
    """
    Tests that the tool applies a custom template file when provided.
    """
    mock_exporter = mock_exporter_class.return_value
    mock_exporter.from_notebook_node.return_value = ("# Exported Python Script with Template", None)

    tool = JupyterExportPythonTool()
    custom_template_path = "path/to/custom_template.tpl"
    result = tool(notebook=mock_notebook, template_file=custom_template_path)

    # Ensure the exporter recognized the template file setting
    assert mock_exporter.template_file == custom_template_path, (
        "PythonExporter.template_file should be set to the provided custom template path."
    )
    assert "exported_script" in result, "Expected 'exported_script' key in the result"


@patch("swarmauri_tool_jupyterexportpython.JupyterExportPythonTool.PythonExporter")
def test_export_notebook_failure(
    mock_exporter_class: MagicMock, mock_notebook: NotebookNode
) -> None:
    """
    Tests that the tool returns an error dictionary when an exception is raised.
    """
    mock_exporter = mock_exporter_class.return_value
    mock_exporter.from_notebook_node.side_effect = Exception("Test failure")

    tool = JupyterExportPythonTool()
    result = tool(notebook=mock_notebook)

    assert "error" in result, "Expected 'error' key in the result due to exception"
    assert "Test failure" in result["error"], "Error message should contain the exception text"


def test_invalid_notebook_input() -> None:
    """
    Tests that the tool handles invalid notebook input gracefully.
    """
    tool = JupyterExportPythonTool()
    result = tool(notebook=None)  # type: ignore

    assert "error" in result, "Expected 'error' key due to invalid notebook input"
    assert "Export failed" in result["error"], (
        "Error message should indicate export failure for invalid input."
    )