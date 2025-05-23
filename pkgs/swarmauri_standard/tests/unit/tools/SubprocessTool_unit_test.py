import platform
import pytest
from swarmauri_standard.tools.SubprocessTool import SubprocessTool as Tool


@pytest.mark.unit
def test_ubc_resource():
    tool = Tool()
    assert tool.resource == "Tool"


@pytest.mark.unit
def test_ubc_type():
    assert Tool().type == "SubprocessTool"


@pytest.mark.unit
def test_initialization():
    tool = Tool()
    assert isinstance(tool.id, str)


@pytest.mark.unit
def test_serialization():
    tool = Tool()
    assert tool.id == Tool.model_validate_json(tool.model_dump_json()).id


@pytest.mark.unit
def test_call():
    system = platform.system().lower()
    if system.startswith("windows"):
        command = "cmd /c echo hello"
    else:
        command = "echo hello"

    tool = Tool()
    result = tool(command=command, shell=True)

    assert result["exit_code"] == "0"
    assert result["stdout"].strip() == "hello"
    assert isinstance(result["stderr"], str)
