import pytest
from unittest.mock import patch

from swarmauri_tool_jupyterdisplayhtml.JupyterDisplayHtmlTool import (
    JupyterDisplayHtmlTool,
)
from swarmauri_base.tools.ToolBase import ToolBase


"""
test_JupyterDisplayHtmlTool.py

This module contains pytest-based test cases for the JupyterDisplayHtmlTool to verify
the functionality and correctness of the class. Each test focuses on different aspects
of the tool's behavior, including instantiation, attribute values, and the handling of
HTML display operations within a Jupyter notebook environment.
"""


@pytest.fixture
def tool() -> JupyterDisplayHtmlTool:
    """
    Provides a fixture that returns a new instance of JupyterDisplayHtmlTool
    for use in multiple tests.
    """
    return JupyterDisplayHtmlTool()


def test_tool_inheritance(tool: JupyterDisplayHtmlTool) -> None:
    """
    Tests that JupyterDisplayHtmlTool inherits from ToolBase, ensuring
    the correct class hierarchy.
    """
    assert isinstance(tool, ToolBase), "Tool should inherit from ToolBase."


def test_tool_attributes(tool: JupyterDisplayHtmlTool) -> None:
    """
    Verifies that the default attributes of JupyterDisplayHtmlTool
    match the expected values.
    """
    assert tool.name == "JupyterDisplayHtmlTool", "Tool name is incorrect."
    assert tool.description == "Renders HTML content within a Jupyter environment.", (
        "Tool description is incorrect."
    )
    assert tool.version == "1.0.0", "Tool version is incorrect."
    assert tool.type == "JupyterDisplayHtmlTool", "Tool type is incorrect."
    assert len(tool.parameters) == 1, "Unexpected number of parameters."
    assert tool.parameters[0].name == "html_content", (
        "First parameter should be 'html_content'."
    )


def test_tool_call_success(tool: JupyterDisplayHtmlTool) -> None:
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


@patch("swarmauri_tool_jupyterdisplayhtml.JupyterDisplayHtmlTool.display")
def test_tool_call_error(mock_display, tool: JupyterDisplayHtmlTool) -> None:
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
