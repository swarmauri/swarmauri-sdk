"""
test_JupyterWriteNotebookTool.py

This module contains pytest-based unit tests for the JupyterWriteNotebookTool class,
ensuring it correctly writes Jupyter notebook data to disk in JSON format and verifies
basic integrity checks.
"""

import os
import json
import pytest
from typing import Dict, Any
from swarmauri_tool_jupyterwritenotebook.JupyterWriteNotebookTool import (
    JupyterWriteNotebookTool,
)


@pytest.fixture
def sample_notebook_data() -> Dict[str, Any]:
    """
    Returns a sample structure representing a minimal Jupyter notebook.
    """
    return {
        "nbformat": 4,
        "nbformat_minor": 5,
        "metadata": {},
        "cells": [
            {"cell_type": "markdown", "metadata": {}, "source": ["# Sample Notebook"]}
        ],
    }


def test_tool_attributes() -> None:
    """
    Tests the basic attributes of JupyterWriteNotebookTool to verify
    it initializes with the expected meta-data.
    """
    tool = JupyterWriteNotebookTool()
    assert tool.name == "JupyterWriteNotebookTool", (
        "Tool name does not match expected value."
    )
    assert tool.type == "JupyterWriteNotebookTool", (
        "Tool type does not match expected value."
    )
    assert tool.version == "1.0.0", "Tool version does not match expected value."
    assert len(tool.parameters) == 3, "Unexpected number of parameters in the tool."
    assert tool.parameters[0].name == "notebook_data", (
        "Expected parameter 'notebook_data' missing."
    )
    assert tool.parameters[1].name == "output_file", (
        "Expected parameter 'output_file' missing."
    )


def test_call_success(
    tmp_path: pytest.TempPathFactory, sample_notebook_data: Dict[str, Any]
) -> None:
    """
    Tests that the tool successfully writes notebook data to a file and
    verifies its integrity by reading it back.
    """
    tool = JupyterWriteNotebookTool()
    output_file = tmp_path / "test_notebook.ipynb"

    result = tool(
        notebook_data=sample_notebook_data,
        output_file=str(output_file),
        encoding="utf-8",
    )

    # Verify that the file was created and the returned message indicates success
    assert "message" in result, f"Expected success message but got: {result}"
    assert "Notebook written successfully" in result["message"], (
        "Success message not found."
    )
    assert os.path.exists(output_file), "Output file does not exist after writing."

    # Verify the written content
    with open(output_file, "r", encoding="utf-8") as f:
        loaded_data = json.load(f)
    assert loaded_data["nbformat"] == 4, "Written notebook data has incorrect nbformat."
    assert loaded_data["nbformat_minor"] == 5, (
        "Written notebook data has incorrect nbformat_minor."
    )


def test_call_empty_notebook_data(tmp_path: pytest.TempPathFactory) -> None:
    """
    Tests that writing an empty notebook data structure still succeeds,
    but logs an error if the verification step fails due to empty content.
    """
    tool = JupyterWriteNotebookTool()
    output_file = tmp_path / "empty_notebook.ipynb"

    empty_data = {}
    result = tool(
        notebook_data=empty_data, output_file=str(output_file), encoding="utf-8"
    )

    # If verification fails, an error key is returned in the result
    assert "error" in result, (
        f"Expected an error for empty notebook data, got: {result}"
    )


def test_call_invalid_file_path(sample_notebook_data: Dict[str, Any]) -> None:
    """
    Tests that providing an invalid file path results in an error.
    """
    tool = JupyterWriteNotebookTool()
    # Using an invalid path (e.g., empty string or invalid characters) should trigger an exception
    result = tool(notebook_data=sample_notebook_data, output_file="", encoding="utf-8")

    assert "error" in result, (
        "Expected an error for an invalid file path but got a success response."
    )
    assert "An error occurred during notebook write operation" in result["error"], (
        "Unexpected error message returned."
    )
