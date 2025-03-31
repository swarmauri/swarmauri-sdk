import platform
from unittest.mock import patch

import pytest

from swarmauri_standard.tools.TestTool import TestTool as Tool


@pytest.mark.unit
def test_ubc_resource():
    tool = Tool()
    assert tool.resource == "Tool"


@pytest.mark.unit
def test_ubc_type():
    assert Tool().type == "TestTool"


@pytest.mark.unit
def test_initialization():
    tool = Tool()
    assert type(tool.id) is str


@pytest.mark.unit
def test_serialization():
    tool = Tool()
    assert tool.id == Tool.model_validate_json(tool.model_dump_json()).id


@pytest.mark.unit
@patch("subprocess.Popen")
def test_call(mock_popen):
    tool = Tool()
    expected_keys = {"program"}
    success_message = "Program Opened: calc"

    result = tool("calc")

    # Platform-dependent assertion
    system = platform.system().lower()
    if system == "darwin":  # macOS
        mock_popen.assert_called_once_with(["open", "-a", "Calculator"])
    elif system == "linux":
        mock_popen.assert_called_once_with(["xcalc"])
    else:  # Windows or other
        mock_popen.assert_called_once_with(["calc"])

    # Rest of the assertions remain the same
    assert isinstance(result, dict)
    assert expected_keys.issubset(result.keys())
    assert isinstance(result.get("program"), str)
    assert result.get("program") == success_message
