from unittest.mock import patch, MagicMock
from swarmauri_tool_jupyterexecutecell.JupyterExecuteCellTool import (
    JupyterExecuteCellTool,
)


def test_tool_initialization():
    """
    Test the initialization of JupyterExecuteCellTool, verifying its default attributes.
    """
    tool = JupyterExecuteCellTool()
    assert tool.name == "JupyterExecuteCellTool", "Tool name should match."
    assert tool.version == "1.0.0", "Tool version should be '1.0.0'."
    assert (
        tool.description == "Executes code cells within a Jupyter kernel environment."
    )

    assert (
        tool.type == "JupyterExecuteCellTool"
    ), "Tool type should be 'JupyterExecuteCellTool'."
    assert (
        len(tool.parameters) == 2
    ), "There should be two default parameters: code, timeout."


def test_tool_parameters():
    """
    Test that the tool's parameter list includes the expected attributes.
    """
    tool = JupyterExecuteCellTool()
    param_names = [param.name for param in tool.parameters]
    assert "code" in param_names, "Parameters must include 'code'."
    assert "timeout" in param_names, "Parameters must include 'timeout'."


def test_tool_call_basic_execution():
    """
    Test that the tool can execute a simple print statement and capture its output.
    """
    tool = JupyterExecuteCellTool()
    result = tool("print('Hello, world!')")
    assert (
        "Hello, world!" in result["stdout"]
    ), "Expected code execution output not found in stdout."
    assert result["stderr"] == "", "stderr should be empty when executing valid code."
    assert result["error"] == "", "error should be empty when executing valid code."


def test_tool_call_syntax_error():
    """
    Test that the tool captures Python syntax errors appropriately.
    """
    tool = JupyterExecuteCellTool()
    result = tool("print('Missing parenthesis'")
    assert (
        "SyntaxError" in result["error"]
    ), "Expected a SyntaxError in the error field."
    assert result["stderr"] != "", "stderr should capture syntax error details."


def test_tool_call_timeout():
    """
    Test that the tool handles code execution timeouts and returns an appropriate error message.
    """
    tool = JupyterExecuteCellTool()
    # This code sleeps for 3 seconds, but we enforce a 1-second timeout to trigger a timeout error.
    result = tool("import time; time.sleep(3)", timeout=1)
    assert (
        "Execution timed out after 1 seconds." in result["error"]
    ), "Expected timeout error message."
    
    assert result["stdout"] == "", "stdout should be empty on timeout."
    assert result["stderr"] == "", "stderr should be empty on timeout."


@patch(
    "swarmauri_tool_jupyterexecutecell.JupyterExecuteCellTool.get_ipython",
    return_value=None,
)
def test_tool_call_no_active_kernel(mock_ipython):
    """
    Test that the tool reports an error when there is no active IPython kernel.
    """
    tool = JupyterExecuteCellTool()
    result = tool("print('Hello')", timeout=1)
    assert (
        result["stderr"] == "No active IPython kernel found."
    ), "Expected stderr to mention no active kernel."
    assert (
        result["error"] == "KernelNotFoundError"
    ), "Expected error to be 'KernelNotFoundError'."
    assert result["stdout"] == "", "stdout should be empty when no kernel is found."


@patch("swarmauri_tool_jupyterexecutecell.JupyterExecuteCellTool.get_ipython")
def test_tool_call_exception_during_execution(mock_ipython):
    """
    Test that the tool captures and logs exceptions raised during code execution.
    """
    # Mock a scenario where run_cell raises an exception.
    mock_shell = MagicMock()
    mock_shell.run_cell.side_effect = RuntimeError("Mocked runtime error")
    mock_ipython.return_value = mock_shell

    tool = JupyterExecuteCellTool()
    result = tool("print('Testing exception')")
    assert (
        "Mocked runtime error" in result["error"]
    ), "Expected mocked runtime error in the error field."
    assert (
        "RuntimeError" in result["error"]
    ), "Expected 'RuntimeError' text in error field."
    assert result["stderr"] != "", "stderr should capture exception details."
    assert (
        "Testing exception" not in result["stdout"]
    ), "stdout should not have content from failing command."
