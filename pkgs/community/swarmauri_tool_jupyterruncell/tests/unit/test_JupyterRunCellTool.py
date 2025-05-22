"""
test_JupyterRunCellTool.py

This module contains pytest-based unit tests for the JupyterRunCellTool class. It verifies
the tool's functionality under various scenarios, including normal execution, error
handling, and timeout handling.
"""

import pytest
import httpx
from swarmauri_tool_jupyterruncell.JupyterRunCellTool import JupyterRunCellTool


class DummyResponse:
    """Simple stand-in for ``httpx.Response``."""

    def __init__(self, json_data, status_code=200):
        self._json = json_data
        self.status_code = status_code

    def json(self):
        return self._json

    def raise_for_status(self):
        if self.status_code >= 400:
            raise httpx.HTTPStatusError("error", request=None, response=None)


def test_jupyter_run_cell_tool_basic(monkeypatch) -> None:
    """
    Test that JupyterRunCellTool successfully executes a simple Python code snippet
    and captures the expected stdout output without errors.
    """
    tool = JupyterRunCellTool()
    code = "print('Hello, test!')"

    def fake_post(url, json, headers=None, timeout=30):
        assert json["code"] == code
        return DummyResponse({"stdout": "Hello, test!\n", "stderr": ""})

    monkeypatch.setattr(httpx, "post", fake_post)

    result = tool(
        code=code,
        base_url="http://server",
        kernel_id="kid",
        timeout=2,
    )

    assert result["success"] is True, "Expected execution success to be True."
    assert "Hello, test!" in result["cell_output"], (
        "Expected 'Hello, test!' in cell output."
    )
    assert result["error_output"] == "", "Expected empty error output."


def test_jupyter_run_cell_tool_error_handling(monkeypatch) -> None:
    """
    Test that JupyterRunCellTool captures exceptions and returns them correctly in the
    error output, setting the success flag to False.
    """
    tool = JupyterRunCellTool()
    code = "raise ValueError('Test error')"

    def fake_post(url, json, headers=None, timeout=30):
        return DummyResponse({"stdout": "", "stderr": "ValueError: Test error"})

    monkeypatch.setattr(httpx, "post", fake_post)

    result = tool(code=code, base_url="http://server", kernel_id="kid", timeout=2)

    assert result["success"] is False, (
        "Expected execution success to be False due to exception."
    )
    assert "ValueError" in result["error_output"], (
        "Expected 'ValueError' in error output."
    )
    assert "Test error" in result["error_output"]


def test_jupyter_run_cell_tool_syntax_error(monkeypatch) -> None:
    """
    Test that JupyterRunCellTool handles syntax errors by capturing the error details
    and setting success to False.
    """
    tool = JupyterRunCellTool()
    code = "This is not valid Python code!"

    def fake_post(url, json, headers=None, timeout=30):
        return DummyResponse({"stdout": "", "stderr": "SyntaxError: invalid syntax"})

    monkeypatch.setattr(httpx, "post", fake_post)

    result = tool(code=code, base_url="http://server", kernel_id="kid", timeout=2)

    assert result["success"] is False, (
        "Expected execution success to be False due to syntax error."
    )
    assert "SyntaxError" in result["error_output"], (
        "Expected 'SyntaxError' in error output."
    )


def test_jupyter_run_cell_tool_timeout(monkeypatch) -> None:
    """
    Test that JupyterRunCellTool respects the timeout parameter and raises a TimeoutError
    if the code execution exceeds the specified limit.
    """
    tool = JupyterRunCellTool()
    code = "print('hi')"

    def fake_post(url, json, headers=None, timeout=30):
        raise httpx.ReadTimeout("timeout")

    monkeypatch.setattr(httpx, "post", fake_post)

    result = tool(code=code, base_url="http://server", kernel_id="kid", timeout=1)

    assert result["success"] is False, "Expected success to be False due to timeout."
    assert "timeout" in result["error_output"]

