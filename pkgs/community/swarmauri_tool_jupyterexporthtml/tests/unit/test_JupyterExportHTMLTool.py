"""
test_JupyterExportHTMLTool.py

This module contains pytest-based test cases for the JupyterExportHTMLTool class, ensuring that
the tool correctly converts Jupyter Notebooks into HTML and properly handles optional parameters
such as template files, extra CSS, and extra JS.
"""

import pytest
from typing import Dict, Any

from swarmauri_tool_jupyterexporthtml.JupyterExportHTMLTool import JupyterExportHTMLTool


@pytest.fixture
def valid_notebook_json() -> str:
    """
    Provides a minimal valid JSON representation of a Jupyter Notebook for testing.
    """
    return (
        '{"cells": [{"cell_type": "markdown", "metadata": {}, "source": ["# Test Notebook"]}],'
        '"metadata": {}, "nbformat": 4, "nbformat_minor": 5}'
    )


@pytest.fixture
def invalid_notebook_json() -> str:
    """
    Provides an intentionally invalid JSON string to test error handling.
    """
    return '{"cells": "this is invalid notebook data"'


def test_jupyter_export_html_tool_instantiation() -> None:
    """
    Tests that the JupyterExportHTMLTool can be instantiated without errors.
    """
    tool = JupyterExportHTMLTool()
    assert tool.name == "JupyterExportHTMLTool"
    assert tool.type == "JupyterExportHTMLTool"
    assert tool.version == "1.0.0"


def test_jupyter_export_html_tool_parameters() -> None:
    """
    Tests that the tool's parameters are defined correctly.
    """
    tool = JupyterExportHTMLTool()
    param_names = [p.name for p in tool.parameters]
    assert "notebook_json" in param_names
    assert "template_file" in param_names
    assert "extra_css" in param_names
    assert "extra_js" in param_names


def test_jupyter_export_html_tool_call_basic(valid_notebook_json: str) -> None:
    """
    Tests calling the JupyterExportHTMLTool with a minimal valid notebook JSON,
    ensuring that it returns a dictionary containing the exported HTML.
    """
    tool = JupyterExportHTMLTool()
    result = tool(notebook_json=valid_notebook_json)
    assert isinstance(result, dict), "Result should be a dictionary."
    assert "exported_html" in result, "The result should contain 'exported_html'."
    assert "<html" in result["exported_html"], (
        "The exported HTML should contain an <html> tag."
    )


def test_jupyter_export_html_tool_call_with_template(valid_notebook_json: str) -> None:
    """
    Tests that providing a template file path is accepted. Since we cannot
    actually load a custom template in a test environment by default, we only
    check that the method runs without raising an exception.
    """
    tool = JupyterExportHTMLTool()
    result = tool(notebook_json=valid_notebook_json, template_file="dummy_template.tpl")
    assert isinstance(result, dict), "Result should be a dictionary."
    # Not testing actual template application here, as we cannot load a real template in this test.


def test_jupyter_export_html_tool_call_with_extra_css(valid_notebook_json: str) -> None:
    """
    Tests that an inline CSS string is correctly embedded in the exported HTML.
    """
    tool = JupyterExportHTMLTool()
    css_content = "body { background-color: #EEE; }"
    result = tool(notebook_json=valid_notebook_json, extra_css=css_content)
    assert "exported_html" in result, "The result should contain 'exported_html'."
    assert css_content in result["exported_html"], (
        "Extra CSS should be present in the exported HTML."
    )


def test_jupyter_export_html_tool_call_with_extra_js(valid_notebook_json: str) -> None:
    """
    Tests that an inline JavaScript string is correctly embedded in the exported HTML.
    """
    tool = JupyterExportHTMLTool()
    js_content = "console.log('Test JS');"
    result = tool(notebook_json=valid_notebook_json, extra_js=js_content)
    assert "exported_html" in result, "The result should contain 'exported_html'."
    assert js_content in result["exported_html"], (
        "Extra JS should be present in the exported HTML."
    )


def test_jupyter_export_html_tool_failure_with_invalid_json(
    invalid_notebook_json: str,
) -> None:
    """
    Tests that providing invalid JSON triggers an error during export.
    """
    tool = JupyterExportHTMLTool()
    result = tool(notebook_json=invalid_notebook_json)
    assert "error" in result, (
        "The result should contain an 'error' key if notebook JSON is invalid."
    )
    assert "An error occurred" in result["error"], (
        "The error message should indicate that an error occurred."
    )


def test_jupyter_export_html_tool_required_parameter() -> None:
    """
    Ensures that the notebook_json parameter is indeed required and an error-like
    result is returned if it is missing or None. The tool uses Pydantic modeling,
    which may raise exceptions if required parameters are missing.
    """
    tool = JupyterExportHTMLTool()
    try:
        result: Dict[str, Any] = tool(notebook_json=None)  # type: ignore
        assert "error" in result, "Expecting an error due to missing notebook_json."
    except Exception as exc:
        # If Pydantic raises an exception, this is also acceptable behavior
        assert "field required" in str(exc), "Missing required field error expected."
