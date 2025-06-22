import pytest
from unittest.mock import patch, MagicMock

from swarmauri_tool_githubloader import GithubLoadedTool
from swarmauri_standard.tools.AdditionTool import AdditionTool
from swarmauri_base.ComponentBase import ComponentBase


@pytest.mark.unit
def test_ubc_resource():
    tool = GithubLoadedTool(owner="o", repo="r", path="p.yaml")
    assert tool.resource == "Tool"


@pytest.mark.unit
def test_ubc_type():
    assert (
        GithubLoadedTool(owner="o", repo="r", path="p.yaml").type == "GithubLoadedTool"
    )


@patch("swarmauri_tool_githubloader.GithubLoadedTool.requests.get")
@pytest.mark.unit
def test_init_loads_metadata(mock_get):
    yaml_content = "type: AdditionTool\nname: LoadedAddTool"
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.text = yaml_content
    mock_get.return_value = mock_resp

    tool = GithubLoadedTool(owner="owner", repo="repo", path="tool.yaml")

    assert isinstance(tool._component, ComponentBase)
    assert tool.name == "LoadedAddTool"
    assert tool.parameters == AdditionTool().parameters


@patch("swarmauri_tool_githubloader.GithubLoadedTool.requests.get")
@pytest.mark.unit
def test_call_uses_cache(mock_get):
    yaml_content = "type: AdditionTool\nname: LoadedAddTool"
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.text = yaml_content
    mock_get.return_value = mock_resp

    tool = GithubLoadedTool(
        owner="owner", repo="repo", path="tool.yaml", use_cache=True
    )
    result = tool(x=1, y=2)

    assert result == {"sum": "3"}
    tool(x=2, y=2)
    mock_get.assert_called_once()


@patch("swarmauri_tool_githubloader.GithubLoadedTool.requests.get")
@pytest.mark.unit
def test_call_without_cache(mock_get):
    yaml_content = "type: AdditionTool\nname: LoadedAddTool"
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.text = yaml_content
    mock_get.return_value = mock_resp

    tool = GithubLoadedTool(
        owner="owner", repo="repo", path="tool.yaml", use_cache=False
    )
    tool(x=1, y=2)
    tool(x=3, y=4)
    assert mock_get.call_count == 2
