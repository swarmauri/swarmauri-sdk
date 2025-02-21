"""
test_JupyterRunCellTool.py

This module contains pytest-based unit tests for the JupyterRunCellTool class. It verifies
the tool's functionality under various scenarios, including normal execution, error
handling, and timeout handling.
"""

import pytest
from swarmauri_tool_jupyterruncell.JupyterRunCellTool import JupyterRunCellTool


# Define a dummy IPython shell that mimics a real shell's run_cell behavior.
class DummyIPythonShell:
    def run_cell(self, code):
        # Execute the code. Exceptions (including SyntaxError and custom exceptions)
        # will propagate, allowing the tool to capture them.
        exec(code, {})


# Automatically patch IPython.get_ipython so that it returns our dummy shell instance.
@pytest.fixture(autouse=True)
def patch_get_ipython(monkeypatch):
    monkeypatch.setattr("IPython.get_ipython", lambda: DummyIPythonShell())


def test_jupyter_run_cell_tool_basic() -> None:
    """
    Test that JupyterRunCellTool successfully executes a simple Python code snippet
    and captures the expected stdout output without errors.
    """
    tool = JupyterRunCellTool()
    code = "print('Hello, test!')"
    result = tool(code=code, timeout=2)

    assert result["success"] is True, "Expected execution success to be True."
    assert (
        "Hello, test!" in result["cell_output"]
    ), "Expected 'Hello, test!' in cell output."
    assert result["error_output"] == "", "Expected empty error output."


def test_jupyter_run_cell_tool_error_handling() -> None:
    """
    Test that JupyterRunCellTool captures exceptions and returns them correctly in the
    error output, setting the success flag to False.
    """
    tool = JupyterRunCellTool()
    code = "raise ValueError('Test error')"
    result = tool(code=code, timeout=2)

    assert (
        result["success"] is False
    ), "Expected execution success to be False due to exception."
    assert (
        "ValueError" in result["error_output"]
    ), "Expected 'ValueError' in error output."
    assert (
        "Test error" in result["error_output"]
    ), "Expected 'Test error' message in error output."


def test_jupyter_run_cell_tool_syntax_error() -> None:
    """
    Test that JupyterRunCellTool handles syntax errors by capturing the error details
    and setting success to False.
    """
    tool = JupyterRunCellTool()
    code = "This is not valid Python code!"
    result = tool(code=code, timeout=2)

    assert (
        result["success"] is False
    ), "Expected execution success to be False due to syntax error."
    assert (
        "SyntaxError" in result["error_output"]
    ), "Expected 'SyntaxError' in error output."


def test_jupyter_run_cell_tool_timeout() -> None:
    """
    Test that JupyterRunCellTool respects the timeout parameter and raises a TimeoutError
    if the code execution exceeds the specified limit.
    """
    tool = JupyterRunCellTool()
    code = """
import time
time.sleep(2)
"""
    result = tool(code=code, timeout=1)

    assert result["success"] is False, "Expected success to be False due to timeout."
    assert (
        "TimeoutError" in result["error_output"]
    ), "Expected 'TimeoutError' in error output."
    assert (
        "Cell execution timed out." in result["error_output"]
    ), "Expected timeout message in error output."
