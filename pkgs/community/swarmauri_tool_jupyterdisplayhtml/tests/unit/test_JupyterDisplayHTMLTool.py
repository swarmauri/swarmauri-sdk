import pytest
from unittest.mock import patch

from swarmauri_tool_jupyterdisplayhtml.JupyterDisplayHTMLTool import (
    JupyterDisplayHTMLTool,
)
from swarmauri_base.tools.ToolBase import ToolBase


"""
test_JupyterDisplayHTMLTool.py

This module contains pytest-based test cases for the JupyterDisplayHTMLTool to verify
the functionality and correctness of the class. Each test focuses on different aspects
of the tool's behavior, including instantiation, attribute values, and the handling of
HTML display operations within a Jupyter notebook environment.
"""


@pytest.fixture
def tool() -> JupyterDisplayHTMLTool:
    """
    Provides a fixture that returns a new instance of JupyterDisplayHTMLTool
    for use in multiple tests.
    """
    return JupyterDisplayHTMLTool()


def test_tool_inheritance(tool: JupyterDisplayHTMLTool) -> None:
    """
    Tests that JupyterDisplayHTMLTool inherits from ToolBase, ensuring
    the correct class hierarchy.
    """
    assert isinstance(tool, ToolBase), "Tool should inherit from ToolBase."


def test_tool_attributes(tool: JupyterDisplayHTMLTool) -> None:
    """
    Verifies that the default attributes of JupyterDisplayHTMLTool
    match the expected values.
    """
    assert tool.name == "JupyterDisplayHTMLTool", "Tool name is incorrect."
    assert tool.description == "Renders HTML content within a Jupyter environment.", (
        "Tool description is incorrect."
    )
    assert tool.version == "1.0.0", "Tool version is incorrect."
    assert tool.type == "JupyterDisplayHTMLTool", "Tool type is incorrect."
    assert len(tool.parameters) == 1, "Unexpected number of parameters."
    assert tool.parameters[0].name == "html_content", (
        "First parameter should be 'html_content'."
    )


def test_tool_call_success(tool: JupyterDisplayHTMLTool) -> None:
    """
    Tests that calling the tool with valid HTML content succeeds and
    returns the expected response dictionary.
    """
    test_html = "<p>Hello, World!</p>"
    result = tool(test_html)
    assert result["status"] == "success", "Expected success status."
    assert "HTML displayed successfully." in result["message"], (
        "Expected success message."
    )


@patch("swarmauri_tool_jupyterdisplayhtml.JupyterDisplayHTMLTool.display")
def test_tool_call_error(mock_display, tool: JupyterDisplayHTMLTool) -> None:
    """
    Tests that the tool handles exceptions during HTML display operations
    by returning an error status and message. The 'display' function is
    patched to raise an exception, simulating a failure scenario.
    """
    mock_display.side_effect = Exception("Simulated display error")
    test_html = "<p>This will fail</p>"
    result = tool(test_html)
    assert result["status"] == "error", "Expected error status."
    assert (
        "An error occurred while displaying HTML: Simulated display error"
        in result["message"]
    ), "Expected error message to contain the simulated exception."
