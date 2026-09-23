import sys

import pytest

from swarmauri_tool_subprocess import SubprocessTool


@pytest.mark.unit
def test_ubc_resource() -> None:
    assert SubprocessTool().resource == "Tool"


@pytest.mark.unit
def test_ubc_type() -> None:
    assert SubprocessTool().type == "SubprocessTool"


@pytest.mark.unit
def test_output_capture() -> None:
    """Capture stdout using the current Python interpreter (cross-platform)."""
    tool = SubprocessTool()
    res = tool([sys.executable, "-c", "print('hello')"])
    assert res["status"] == "success"
    assert "hello" in str(res["stdout"])


@pytest.mark.unit
def test_nonzero_exit() -> None:
    tool = SubprocessTool()
    res = tool([sys.executable, "-c", "import sys; sys.exit(1)"])
    assert res["exit_code"] == 1
    assert res["status"] == "success"


@pytest.mark.unit
def test_missing_executable() -> None:
    tool = SubprocessTool()
    res = tool("this_command_does_not_exist_xyz")
    assert res["status"] == "not_found"
    assert res["exit_code"] == 127
    assert "not found" in str(res["stderr"]).lower()


@pytest.mark.unit
def test_timeout_behavior() -> None:
    tool = SubprocessTool()
    res = tool(
        [sys.executable, "-c", "import time; time.sleep(5)"],
        timeout=0.5,
    )
    assert res["status"] == "timeout"
    assert res["exit_code"] is None


@pytest.mark.unit
def test_argument_quoting_whitespace() -> None:
    """Argument vectors must preserve embedded whitespace."""
    tool = SubprocessTool()
    res = tool(
        [sys.executable, "-c", "import sys; print(sys.argv[1])", "hello world"]
    )
    assert res["status"] == "success"
    assert "hello world" in str(res["stdout"])