"""Regression proofs for the original case-sensitive import and results."""

import importlib
import sys
from unittest.mock import patch

import pytest


def _legacy_tool():
    module = importlib.import_module("swarmauri_standard.tools.SubprocessTool")
    return module.SubprocessTool()


@pytest.mark.unit
def test_module_import_is_lazy() -> None:
    module = importlib.import_module("swarmauri_standard.tools.SubprocessTool")
    spec = importlib.util.spec_from_file_location(
        "legacy_probe", module.__file__
    )
    fresh = importlib.util.module_from_spec(spec)
    with patch.dict(sys.modules, {"swarmauri_tool_subprocess": None}):
        spec.loader.exec_module(fresh)
    assert "SubprocessTool" not in vars(fresh)


@pytest.mark.unit
def test_original_import_and_string_exit_status() -> None:
    tool = _legacy_tool()
    result = tool("echo 123", shell=True)
    assert result == {"stdout": "123\n", "stderr": "", "exit_code": "0"}
    assert set(result) == {"stdout", "stderr", "exit_code"}


@pytest.mark.unit
@pytest.mark.parametrize(
    ("status", "code", "expected"),
    [
        ("success", 7, "7"),
        ("timeout", None, "timeout"),
        ("not_found", 127, "error"),
        ("runtime_error", None, "error"),
    ],
)
def test_legacy_status_mapping(status, code, expected) -> None:
    from swarmauri_standard.tools import _subprocess

    tool = _legacy_tool()
    with patch.object(
        _subprocess,
        "run_subprocess",
        return_value={
            "status": status,
            "stdout": "",
            "stderr": "detail",
            "exit_code": code,
        },
    ):
        result = tool("unused")
    assert result["exit_code"] == expected
    if status == "timeout":
        assert result["stderr"] == "Process timed out"


@pytest.mark.unit
def test_malformed_legacy_command_returns_error() -> None:
    assert _legacy_tool()('"unterminated')["exit_code"] == "error"


@pytest.mark.unit
def test_legacy_identity_and_serialization() -> None:
    tool = _legacy_tool()
    restored = type(tool).model_validate_json(tool.model_dump_json())
    assert restored.id == tool.id
    assert restored.name == "SubprocessTool"
    assert restored.type == "SubprocessTool"
    assert restored.resource == "Tool"


@pytest.mark.unit
def test_legacy_case_spellings_share_the_same_module() -> None:
    upper = importlib.import_module("swarmauri_standard.tools.SubprocessTool")
    lower = importlib.import_module("swarmauri_standard.tools.subprocessTool")
    assert lower is upper
    assert lower.SubprocessTool is upper.SubprocessTool


@pytest.mark.unit
def test_legacy_schema_and_execution_with_only_the_kernel() -> None:
    with patch.dict(sys.modules, {"swarmauri_tool_subprocess": None}):
        tool = _legacy_tool()
        assert [field.name for field in tool.parameters] == [
            "command",
            "timeout",
            "shell",
        ]
        assert tool("echo 123", shell=True)["exit_code"] == "0"
