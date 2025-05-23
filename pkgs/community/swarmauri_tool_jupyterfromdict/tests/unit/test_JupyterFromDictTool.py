"""
test_JupyterFromDictTool.py

This module contains pytest-based unit tests for the JupyterFromDictTool class. It verifies that
the class correctly converts dictionary data into a validated Jupyter NotebookNode and handles
errors appropriately.
"""

from nbformat import NotebookNode
from swarmauri_tool_jupyterfromdict.JupyterFromDictTool import JupyterFromDictTool
from unittest.mock import patch


def test_class_attributes() -> None:
    """
    Tests the static attributes of the JupyterFromDictTool class to ensure they match expectations.
    """
    tool = JupyterFromDictTool()
    assert tool.version == "1.0.0", "Tool version should match expected value."
    assert tool.name == "JupyterFromDictTool", (
        "Tool name should be JupyterFromDictTool."
    )
    assert (
        tool.description
        == "Converts a dictionary into a validated Jupyter NotebookNode."
    )
    assert tool.type == "JupyterFromDictTool", (
        "Tool type should match the expected literal string."
    )
    assert len(tool.parameters) == 1, "Expected exactly one parameter in the tool."
    assert tool.parameters[0].name == "notebook_dict", (
        "Parameter name should be 'notebook_dict'."
    )


def test_call_with_valid_notebook_dict() -> None:
    """
    Tests calling the tool with a valid notebook dictionary to ensure it returns a valid NotebookNode.
    """
    tool = JupyterFromDictTool()
    valid_notebook_dict = {
        "nbformat": 4,
        "nbformat_minor": 5,
        "cells": [],
        "metadata": {},
    }

    result = tool(valid_notebook_dict)

    assert "notebook_node" in result, "Result should contain a 'notebook_node' key."
    assert isinstance(result["notebook_node"], NotebookNode), (
        "Result's 'notebook_node' should be an instance of nbformat.NotebookNode."
    )


def test_call_with_invalid_notebook_dict() -> None:
    """
    Tests calling the tool with an invalid notebook dictionary to ensure it returns an error message.
    """
    tool = JupyterFromDictTool()
    invalid_notebook_dict = {
        # Missing nbformat key, which is required
        "cells": [],
        "metadata": {},
    }

    result = tool(invalid_notebook_dict)

    assert "error" in result, (
        "Result should contain an 'error' key for an invalid notebook dict."
    )
    assert "validation error" in result["error"].lower(), (
        "Error message should indicate a validation error for an invalid notebook."
    )


def test_call_with_exception_handling() -> None:
    """Ensure a generic exception is handled gracefully."""
    tool = JupyterFromDictTool()

    with patch("nbformat.from_dict", side_effect=Exception("Mock failure")):
        result = tool({})

    assert "error" in result
    assert result["error"] == "An error occurred: Mock failure"
