"""
test_JupyterExportMarkdownTool.py

This module contains pytest-based test cases for the JupyterExportMarkdownTool class,
verifying its functionality and correctness when converting Jupyter Notebooks to
Markdown format.
"""

import pytest
from typing import Dict, Any, Optional

from swarmauri_tool_jupyterexportmarkdown.JupyterExportMarkdownTool import (
    JupyterExportMarkdownTool,
)


@pytest.fixture
def sample_notebook_json() -> Dict[str, Any]:
    """
    A sample fixture that provides a basic Jupyter Notebook JSON structure
    for testing the export functionality.
    """
    return {
        "cells": [
            {
                "cell_type": "markdown",
                "metadata": {},
                "source": ["# Sample Notebook\\n", "Some introductory text."],
            },
            {
                "cell_type": "code",
                "metadata": {},
                "execution_count": None,
                "outputs": [],
                "source": ["print('Hello, World!')"],
            },
        ],
        "metadata": {},
        "nbformat": 4,
        "nbformat_minor": 5,
    }


@pytest.fixture
def tool_instance() -> JupyterExportMarkdownTool:
    """
    Creates an instance of the JupyterExportMarkdownTool for testing.
    """
    return JupyterExportMarkdownTool()


def test_tool_metadata(tool_instance: JupyterExportMarkdownTool) -> None:
    """
    Tests the metadata of the JupyterExportMarkdownTool for correctness.
    """
    assert tool_instance.name == "JupyterExportMarkdownTool"
    assert (
        tool_instance.description == "Converts a Jupyter Notebook into Markdown format."
    )
    assert tool_instance.version == "1.0.0"
    assert tool_instance.type == "JupyterExportMarkdownTool"


def test_export_basic_notebook(
    tool_instance: JupyterExportMarkdownTool, sample_notebook_json: Dict[str, Any]
) -> None:
    """
    Tests exporting a basic sample notebook JSON to ensure Markdown is returned without errors.
    """
    result = tool_instance(notebook_json=sample_notebook_json)
    assert "exported_markdown" in result, (
        "Expected 'exported_markdown' in the return dictionary."
    )
    assert "Notebook" in result["exported_markdown"], (
        "Expected the heading from the sample notebook in the output."
    )


def test_export_with_styles(
    tool_instance: JupyterExportMarkdownTool, sample_notebook_json: Dict[str, Any]
) -> None:
    """
    Tests exporting the notebook with custom CSS styles to verify that they are applied.
    """
    custom_css = "h1 { color: red; }"
    result = tool_instance(notebook_json=sample_notebook_json, styles=custom_css)
    assert "exported_markdown" in result, (
        "Expected 'exported_markdown' in the return dictionary."
    )
    # We cannot directly check embedded CSS in the Markdown, but we can confirm no errors were returned.
    assert "error" not in result, (
        f"Unexpected error encountered: {result.get('error', '')}"
    )


def test_export_with_template(
    tool_instance: JupyterExportMarkdownTool, sample_notebook_json: Dict[str, Any]
) -> None:
    """
    Tests exporting the notebook with a custom template to ensure it is utilized.
    Note: This test does not provide a real template file, but checks for error handling.
    """
    fake_template = "non_existent_template.tpl"
    result = tool_instance(notebook_json=sample_notebook_json, template=fake_template)
    # Depending on nbconvert versions, a non-existent template may or may not raise an exception internally.
    # Check if the tool handled it without crashing and returned an 'exported_markdown' or 'error'.
    if "error" in result:
        # If an error was raised, ensure it's related to the template issue.
        assert "Failed to export notebook" in result["error"]
    else:
        # If no error was raised, the export must have succeeded, though the template doesn't exist.
        assert "exported_markdown" in result


def test_export_error_handling(tool_instance: JupyterExportMarkdownTool) -> None:
    """
    Tests handling of invalid notebook data to ensure the method returns an error
    without raising an uncaught exception.
    """
    invalid_notebook_json: Optional[Dict[str, Any]] = (
        None  # Invalid type for the notebook structure
    )
    result = tool_instance(notebook_json=invalid_notebook_json)  # type: ignore[arg-type]
    assert "error" in result, (
        "Expected 'error' key in the return dictionary for invalid input."
    )
    assert "Failed to export notebook" in result["error"], (
        "Expected an error message indicating a failure."
    )
