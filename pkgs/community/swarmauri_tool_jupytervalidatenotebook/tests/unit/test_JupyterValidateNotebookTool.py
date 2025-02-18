"""
test_JupyterValidateNotebookTool.py

Pytest based unit tests for JupyterValidateNotebookTool from
swarmauri_tool_jupytervalidatenotebook.JupyterValidateNotebookTool.
This file ensures that the tool behaves correctly for valid and invalid notebooks,
and checks various attributes and features of the class.
"""

import pytest
import nbformat
from nbformat import NotebookNode
from nbformat.validator import NotebookValidationError
from swarmauri_tool_jupytervalidatenotebook.JupyterValidateNotebookTool import (
    JupyterValidateNotebookTool,
)
from swarmauri_base.tools.ToolBase import ToolBase

def test_class_inheritance() -> None:
    """
    Test whether JupyterValidateNotebookTool inherits from ToolBase.
    """
    tool = JupyterValidateNotebookTool()
    assert isinstance(tool, ToolBase), "JupyterValidateNotebookTool should inherit from ToolBase."


def test_class_attributes() -> None:
    """
    Test the existence and correctness of class attributes.
    """
    tool = JupyterValidateNotebookTool()
    assert tool.version == "1.0.0", "Version attribute should be '1.0.0'."
    assert tool.name == "JupyterValidateNotebookTool", "Name attribute mismatch."
    assert tool.description == "Validates a Jupyter notebook structure against its JSON schema."
    assert tool.type == "JupyterValidateNotebookTool", "Type attribute mismatch."
    assert len(tool.parameters) == 1, "Should have exactly one parameter definition."
    assert tool.parameters[0].name == "notebook", "Parameter name should be 'notebook'."


def test_valid_notebook_validation() -> None:
    """
    Test the validation process with a valid notebook. Expecting a success response.
    """
    # Create a valid minimal notebook
    valid_notebook: NotebookNode = nbformat.v4.new_notebook()
    valid_notebook["cells"] = [nbformat.v4.new_markdown_cell("Test")]

    tool = JupyterValidateNotebookTool()
    result = tool(valid_notebook)

    assert result["valid"] == "True", "Valid notebook should return 'True'."
    assert "The notebook is valid" in result["report"], "Report should indicate successful validation."


def test_invalid_notebook_validation() -> None:
    """
    Test the validation process with an invalid notebook. Expecting a failure response.
    """
    # Create a notebook with an invalid nbformat field (should be an integer)
    invalid_notebook: NotebookNode = nbformat.v4.new_notebook()
    invalid_notebook["nbformat"] = "invalid"  # This should trigger a NotebookValidationError

    tool = JupyterValidateNotebookTool()
    result = tool(invalid_notebook)

    assert result["valid"] == "False", "Invalid notebook should return 'False'."
    assert "Validation error:" in result["report"], "Report should contain the validation error message."


def test_unexpected_error_handling(monkeypatch) -> None:
    """
    Test how the tool handles unexpected errors during validation.
    We monkeypatch nbformat.validate to raise a general exception.
    """
    tool = JupyterValidateNotebookTool()

    def fake_validate(notebook, **kwargs):
        raise RuntimeError("Unexpected runtime error!")

    monkeypatch.setattr(nbformat, "validate", fake_validate)

    notebook: NotebookNode = nbformat.v4.new_notebook()
    notebook["cells"] = [nbformat.v4.new_markdown_cell("Test")]

    result = tool(notebook)

    assert result["valid"] == "False", "Should return 'False' on unexpected error."
    assert "Unexpected error:" in result["report"], "Report should indicate an unexpected error."
    assert "Unexpected runtime error!" in result["report"], "Should capture the actual error message."
