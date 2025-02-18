"""
test_JupyterExportLatexTool.py

This module contains pytest-based test cases for verifying the functionality of the
JupyterExportLatexTool class. It checks the correctness of the LaTeX conversion process
and optional PDF generation, as well as error handling for problematic inputs.
"""

import os
import pytest
from typing import Dict, Any
from nbformat.v4.nbbase import new_notebook
from swarmauri_tool_jupyterexportlatex.JupyterExportLatexTool import JupyterExportLatexTool
from swarmauri_base.tools.ToolBase import ToolBase


@pytest.fixture
def sample_notebook_node() -> Any:
    """
    Provides a sample NotebookNode object for testing.

    Returns:
        A simple NotebookNode containing one empty cell.
    """
    nb = new_notebook()
    nb.cells.append({"cell_type": "code", "source": [], "metadata": {}, "outputs": []})
    return nb


def test_jupyter_export_latex_tool_inheritance() -> None:
    """
    Ensures that JupyterExportLatexTool inherits from the ToolBase class.
    """
    assert issubclass(JupyterExportLatexTool, ToolBase), (
        "JupyterExportLatexTool does not inherit from ToolBase as expected."
    )


def test_jupyter_export_latex_tool_init() -> None:
    """
    Tests default initialization of the JupyterExportLatexTool class.
    Verifies that the default attributes match expected values.
    """
    tool = JupyterExportLatexTool()
    assert tool.version == "0.1.0", "Default version should be '0.1.0'."
    assert tool.name == "JupyterExportLatexTool", "Tool name should match its class name."
    assert tool.type == "JupyterExportLatexTool", (
        "Tool type should be 'JupyterExportLatexTool'."
    )


def test_conversion_no_custom_template_no_pdf(sample_notebook_node: Any) -> None:
    """
    Tests the LaTeX conversion process without a custom template and without PDF generation.
    Ensures that the returned dictionary contains LaTeX content and no errors.
    """
    tool = JupyterExportLatexTool()
    result: Dict[str, Any] = tool(
        notebook_node=sample_notebook_node,
        use_custom_template=False,
        to_pdf=False
    )
    assert "error" not in result, f"Error returned unexpectedly: {result.get('error', '')}"
    assert "latex_content" in result, "Expected 'latex_content' key in the result."
    assert result["latex_content"], "LaTeX content should not be empty."


def test_conversion_no_custom_template_with_pdf(sample_notebook_node: Any) -> None:
    """
    Tests the LaTeX conversion process without a custom template and with PDF generation.
    Ensures that the returned dictionary includes a PDF path.
    """
    tool = JupyterExportLatexTool()
    result: Dict[str, Any] = tool(
        notebook_node=sample_notebook_node,
        use_custom_template=False,
        to_pdf=True
    )
    assert "error" not in result, f"Error returned unexpectedly: {result.get('error', '')}"
    assert "latex_content" in result, "Missing 'latex_content' in the result."
    assert "pdf_file_path" in result, "Missing 'pdf_file_path' in the result."
    assert os.path.isfile(result["pdf_file_path"]), (
        "The PDF file path does not point to a valid file."
    )


def test_conversion_with_custom_template(sample_notebook_node: Any, tmp_path) -> None:
    """
    Tests the LaTeX conversion process with a custom template. Verifies that the tool
    accepts a template path and processes the notebook without raising an error.

    Args:
        sample_notebook_node (Any): A fixture providing a minimal NotebookNode.
        tmp_path: A pytest fixture providing a temporary directory.
    """
    # Create a dummy template file
    custom_template = tmp_path / "custom.tplx"
    custom_template.write_text("Some custom LaTeX template content")

    tool = JupyterExportLatexTool()
    result: Dict[str, Any] = tool(
        notebook_node=sample_notebook_node,
        use_custom_template=True,
        template_path=str(custom_template),
        to_pdf=False
    )
    assert "error" not in result, f"Error returned unexpectedly with custom template: {result.get('error', '')}"
    assert "latex_content" in result, "Expected 'latex_content' key in the result (custom template)."


def test_conversion_error_handling() -> None:
    """
    Tests that the tool handles conversion errors gracefully and returns an error message
    when given invalid input instead of a NotebookNode.
    """
    tool = JupyterExportLatexTool()
    result: Dict[str, Any] = tool(
        notebook_node=None,  # Invalid
        use_custom_template=False,
        template_path=None,
        to_pdf=False
    )
    assert "error" in result, "Expected an error message for invalid notebook input."
    assert "latex_content" not in result, "There should be no 'latex_content' for invalid input."