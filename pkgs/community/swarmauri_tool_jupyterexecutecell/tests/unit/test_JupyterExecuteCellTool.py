import pytest

from swarmauri_tool_jupyterexecutecell.JupyterExecuteCellTool import JupyterExecuteCellTool


@pytest.mark.unit
def test_tool_initialization() -> None:
    """Verify the tool's default attributes."""
    tool = JupyterExecuteCellTool()
    assert tool.name == "JupyterExecuteCellTool"
    assert tool.version == "1.0.0"
    assert tool.type == "JupyterExecuteCellTool"
    assert len(tool.parameters) == 2


@pytest.mark.unit
def test_tool_parameters() -> None:
    """Ensure kernel_id and code parameters exist."""
    tool = JupyterExecuteCellTool()
    param_names = {p.name for p in tool.parameters}
    assert {"kernel_id", "code"} <= param_names


@pytest.mark.unit
def test_tool_call_basic_execution() -> None:
    """Execute simple code and capture stdout."""
    tool = JupyterExecuteCellTool()
    result = tool("dummy", "print('Hello, world!')")
    assert "Hello, world!" in result["stdout"]
    assert result["stderr"] == ""
    assert result["error"] == ""


@pytest.mark.unit
def test_tool_call_syntax_error() -> None:
    """Return syntax errors from invalid code."""
    tool = JupyterExecuteCellTool()
    result = tool("dummy", "print('Missing'")
    assert "SyntaxError" in result["error"]
    assert result["stderr"] == ""


@pytest.mark.unit
def test_tool_call_runtime_error() -> None:
    """Handle exceptions raised during execution."""
    tool = JupyterExecuteCellTool()
    result = tool("dummy", "raise RuntimeError('boom')")
    assert "RuntimeError" in result["error"]
    assert "boom" in result["error"]
    assert result["stdout"] == ""


@pytest.mark.unit
def test_tool_call_no_kernel(monkeypatch) -> None:
    """Gracefully handle errors raised by the REST client."""

    def raise_error(kernel_id: str, code: str):
        raise RuntimeError("Kernel not found")

    monkeypatch.setattr(
        "swarmauri_tool_jupyterexecutecell.jupyter_rest_client.execute_cell",
        raise_error,
    )

    tool = JupyterExecuteCellTool()
    result = tool("bad", "print('hi')")
    assert result["error"] == "Kernel not found"
    assert result["stdout"] == ""
    assert result["stderr"] == ""
