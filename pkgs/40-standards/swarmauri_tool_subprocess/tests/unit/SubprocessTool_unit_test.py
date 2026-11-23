import sys
import time
import os
from importlib.metadata import entry_points
from unittest.mock import patch

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


@pytest.mark.unit
def test_component_identity_and_serialization() -> None:
    tool = SubprocessTool()
    restored = SubprocessTool.model_validate_json(tool.model_dump_json())
    assert tool.name == "SubprocessTool"
    assert isinstance(tool.id, str)
    assert restored.id == tool.id
    assert restored.type == "SubprocessTool"


@pytest.mark.unit
def test_dynamic_registration() -> None:
    from swarmauri_base.DynamicBase import DynamicBase

    assert (
        DynamicBase._registry["ToolBase"]["subtypes"]["SubprocessTool"]
        is SubprocessTool
    )


@pytest.mark.unit
def test_installed_entry_point() -> None:
    points = entry_points(group="swarmauri.tools", name="SubprocessTool")
    assert any(point.load() is SubprocessTool for point in points)


@pytest.mark.unit
@pytest.mark.parametrize("command", ['"unterminated', "", [], [1]])
def test_invalid_commands_return_runtime_errors(command) -> None:
    result = SubprocessTool()(command)
    assert result["status"] == "runtime_error"
    assert result["exit_code"] is None


@pytest.mark.unit
def test_shell_argument_lists_are_rejected_without_execution() -> None:
    with patch("subprocess.run") as run:
        result = SubprocessTool()(["echo", "hello"], shell=True)
    run.assert_not_called()
    assert result["status"] == "runtime_error"


@pytest.mark.unit
def test_shell_metacharacters_are_literal_by_default() -> None:
    result = SubprocessTool()(
        [sys.executable, "-c", "import sys; print(sys.argv[1])", "a; echo b"]
    )
    assert result["stdout"].strip() == "a; echo b"


@pytest.mark.unit
def test_shell_strings_use_the_platform_shell() -> None:
    result = SubprocessTool()("echo first && echo second", shell=True)
    assert result["exit_code"] == 0
    assert result["stdout"].split() == ["first", "second"]


@pytest.mark.unit
def test_custom_directory(tmp_path) -> None:
    result = SubprocessTool()(
        [sys.executable, "-c", "import os; print(os.getcwd())"],
        cwd=str(tmp_path),
    )
    assert os.path.samefile(result["stdout"].strip(), tmp_path)


@pytest.mark.unit
def test_environment_is_replaced_not_merged(monkeypatch) -> None:
    monkeypatch.setenv("SWARMAURI_PARENT_ONLY", "private")
    child_env = {
        key: value
        for key, value in os.environ.items()
        if key != "SWARMAURI_PARENT_ONLY"
    }
    child_env["SWARMAURI_CHILD_ONLY"] = "explicit"
    result = SubprocessTool()(
        [
            sys.executable,
            "-c",
            "import os; print(os.getenv('SWARMAURI_PARENT_ONLY')); "
            "print(os.getenv('SWARMAURI_CHILD_ONLY'))",
        ],
        env=child_env,
    )
    assert result["stdout"].splitlines() == ["None", "explicit"]


@pytest.mark.unit
def test_timeout_kills_and_waits_for_the_direct_child(tmp_path) -> None:
    marker = tmp_path / "late.txt"
    result = SubprocessTool()(
        [
            sys.executable,
            "-c",
            "import pathlib, sys, time; time.sleep(0.3); "
            "pathlib.Path(sys.argv[1]).write_text('unexpected')",
            str(marker),
        ],
        timeout=0.05,
    )
    # A second child supplies a bounded delay before checking for late effects.
    import subprocess

    subprocess.run(
        [sys.executable, "-c", "import time; time.sleep(0.4)"], check=True
    )
    assert result["status"] == "timeout"
    assert not marker.exists()


@pytest.mark.unit
@pytest.mark.skipif(os.name != "nt", reason="Windows executable resolution")
def test_native_mode_rejects_batch_paths_and_search_results(
    tmp_path, monkeypatch
):
    batch = tmp_path / "probe.cmd"
    batch.write_bytes(b"@echo off\r\nexit /b 0\r\n")
    monkeypatch.setenv("PATH", str(tmp_path))
    monkeypatch.setenv("PATHEXT", ".EXE;.CMD;.BAT")
    result = SubprocessTool()([str(batch), "x&ver"])
    assert result["status"] == "runtime_error"
    assert "native .exe" in result["stderr"]
    assert SubprocessTool()(["probe", "x&ver"])["status"] == "not_found"


@pytest.mark.unit
@pytest.mark.skipif(os.name != "nt", reason="Windows executable resolution")
def test_native_search_includes_system_directory(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv("PATH", str(tmp_path))
    assert SubprocessTool()(["whoami.exe"], timeout=5)["exit_code"] == 0
    assert SubprocessTool()(["tree.com", "/?"], timeout=5)["exit_code"] == 0


@pytest.mark.unit
@pytest.mark.skipif(
    os.name != "nt", reason="Windows inherited capture handles"
)
def test_timed_call_does_not_wait_for_descendant_output_handle(tmp_path):
    marker = tmp_path / "started"
    parent = (
        "import pathlib, subprocess, sys, time;"
        "subprocess.Popen([sys.executable, '-c',"
        "'import time; time.sleep(4)']);"
        "pathlib.Path(sys.argv[1]).touch();"
        "time.sleep(4)"
    )
    start = time.monotonic()
    result = SubprocessTool()(
        [sys.executable, "-c", parent, str(marker)], timeout=1.5
    )
    assert marker.exists()
    assert result["status"] == "timeout"
    assert time.monotonic() - start < 3.5


@pytest.mark.unit
@pytest.mark.skipif(os.name != "nt", reason="Windows file capture")
def test_timed_windows_call_captures_text_and_normalizes_newlines():
    result = SubprocessTool()(
        [
            sys.executable,
            "-c",
            "import sys; print('out'); print('err', file=sys.stderr)",
        ],
        timeout=5,
    )
    assert result == {
        "status": "success",
        "stdout": "out\n",
        "stderr": "err\n",
        "exit_code": 0,
    }
