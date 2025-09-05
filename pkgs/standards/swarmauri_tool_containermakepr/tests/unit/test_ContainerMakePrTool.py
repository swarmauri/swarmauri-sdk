from unittest.mock import MagicMock, patch

import pytest
from swarmauri_tool_containermakepr import ContainerMakePrTool as Tool


@pytest.mark.unit
def test_ubc_resource():
    assert Tool().resource == "Tool"


@pytest.mark.unit
def test_ubc_type():
    assert Tool().type == "ContainerMakePrTool"


@pytest.mark.unit
def test_initialization():
    assert isinstance(Tool().id, str)


@pytest.mark.unit
def test_serialization():
    tool = Tool()
    assert tool.id == Tool.model_validate_json(tool.model_dump_json()).id


@pytest.mark.unit
@patch("subprocess.run")
def test_call(mock_run):
    mock_run.return_value = MagicMock(returncode=0, stdout="created", stderr="")
    tool = Tool(container_name="c1")
    result = tool(title="t", body="b")
    mock_run.assert_called_once()
    assert result["stdout"] == "created"
