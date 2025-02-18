import os
import pytest
import subprocess
from unittest.mock import patch, MagicMock
from swarmauri_tool_jupyterexecuteandconvert.JupyterExecuteAndConvertTool import JupyterExecuteAndConvertTool


@pytest.fixture
def tool_instance() -> JupyterExecuteAndConvertTool:
    """
    Pytest fixture to create an instance of JupyterExecuteAndConvertTool.
    """
    return JupyterExecuteAndConvertTool()


def test_tool_attributes(tool_instance: JupyterExecuteAndConvertTool) -> None:
    """
    Test that the JupyterExecuteAndConvertTool instance has the expected attributes.
    """
    assert tool_instance.name == "JupyterExecuteAndConvertTool"
    assert tool_instance.description == "Executes a Jupyter notebook and converts it to a specified format."
    assert tool_instance.type == "JupyterExecuteAndConvertTool"
    assert len(tool_instance.parameters) == 3


def test_notebook_not_found(tool_instance: JupyterExecuteAndConvertTool) -> None:
    """
    Test that providing a non-existent notebook path returns an error indicating the file does not exist.
    """
    result = tool_instance(
        notebook_path="non_existent_notebook.ipynb",
        output_format="html",
        execution_timeout=10
    )
    assert "error" in result
    assert result["error"] == "Notebook file does not exist."


@patch("subprocess.run")
def test_successful_execution_and_conversion(mock_subprocess: MagicMock, tool_instance: JupyterExecuteAndConvertTool) -> None:
    """
    Test successful execution and conversion of a notebook by mocking subprocess.run.
    Ensures the tool returns a dictionary with status 'success' and the correct converted file name.
    """
    # Mock to simulate successful execution and conversion
    mock_subprocess.return_value = None

    # Create a temporary notebook file for the sake of the test
    temp_notebook = "test_notebook.ipynb"
    with open(temp_notebook, "w", encoding="utf-8") as f:
        f.write("# Test notebook content")

    result = tool_instance(
        notebook_path=temp_notebook,
        output_format="html",
        execution_timeout=10
    )

    # Clean up the temporary file
    os.remove(temp_notebook)

    assert "status" in result
    assert result["status"] == "success"
    assert "converted_file" in result
    assert result["converted_file"].endswith(".html")


@patch("subprocess.run")
def test_execution_timeout(mock_subprocess: MagicMock, tool_instance: JupyterExecuteAndConvertTool) -> None:
    """
    Test that a TimeoutExpired exception is handled properly.
    Ensures the tool returns an error dictionary with the appropriate keys.
    """
    # Mock to raise TimeoutExpired
    mock_subprocess.side_effect = subprocess.TimeoutExpired(cmd="jupyter nbconvert", timeout=5)

    temp_notebook = "timeout_notebook.ipynb"
    with open(temp_notebook, "w", encoding="utf-8") as f:
        f.write("# Test notebook content for timeout")

    result = tool_instance(
        notebook_path=temp_notebook,
        output_format="html",
        execution_timeout=1
    )

    os.remove(temp_notebook)

    assert "error" in result
    assert result["error"] == "TimeoutExpired"


@patch("subprocess.run")
def test_execution_error(mock_subprocess: MagicMock, tool_instance: JupyterExecuteAndConvertTool) -> None:
    """
    Test that a CalledProcessError during notebook execution is handled properly.
    Ensures the tool returns an error dictionary with the appropriate keys.
    """
    # Mock to raise CalledProcessError for execution
    mock_subprocess.side_effect = subprocess.CalledProcessError(
        returncode=1, cmd="jupyter nbconvert"
    )

    temp_notebook = "fail_notebook.ipynb"
    with open(temp_notebook, "w", encoding="utf-8") as f:
        f.write("# Test notebook content for execution error")

    result = tool_instance(
        notebook_path=temp_notebook,
        output_format="html",
        execution_timeout=10
    )

    os.remove(temp_notebook)

    assert "error" in result
    assert result["error"] == "ExecutionError"


@patch("subprocess.run")
def test_conversion_error(mock_subprocess: MagicMock, tool_instance: JupyterExecuteAndConvertTool) -> None:
    """
    Test that a CalledProcessError during notebook conversion is handled properly.
    Ensures the tool returns an error dictionary with the appropriate keys.
    """
    # First run: simulate successful notebook execution
    call_effects = [
        None,  # Successful execution
        subprocess.CalledProcessError(returncode=2, cmd="jupyter nbconvert")  # Conversion fails
    ]
    mock_subprocess.side_effect = call_effects

    temp_notebook = "conversion_fail_notebook.ipynb"
    with open(temp_notebook, "w", encoding="utf-8") as f:
        f.write("# Test notebook content for conversion error")

    result = tool_instance(
        notebook_path=temp_notebook,
        output_format="html",
        execution_timeout=10
    )

    os.remove(temp_notebook)

    assert "error" in result
    assert result["error"] == "ConversionError"