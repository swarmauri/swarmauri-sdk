import os
from unittest.mock import patch, MagicMock
import pytest
import logging
from swarmauri_standard.tools.AdditionTool import AdditionTool
from swarmauri_tool_github.GithubRepoTool import GithubRepoTool
from swarmauri_tool_github.GithubToolkit import GithubToolkit as Toolkit
from dotenv import load_dotenv

load_dotenv()


@pytest.fixture(scope="module")
def github_token():
    token = os.getenv("GITHUBTOOL_TEST_TOKEN")
    if not token:
        pytest.skip("Skipping due to GITHUBTOOL_TEST_TOKEN not set")
    return token


@pytest.fixture(scope="module")
def github_toolkit(github_token):
    return Toolkit(token=github_token)


@pytest.mark.unit
def test_ubc_resource(github_toolkit):
    assert github_toolkit.resource == "GithubToolkit"


@pytest.mark.unit
def test_ubc_type(github_toolkit):
    assert github_toolkit.type == "GithubToolkit"


@pytest.mark.unit
def test_serialization(github_toolkit):
    serialized_data = github_toolkit.model_dump_json()
    deserialized_toolkit = Toolkit.model_validate_json(serialized_data)
    assert github_toolkit.id == deserialized_toolkit.id


@pytest.mark.unit
def test_tool_count(github_toolkit):
    assert len(github_toolkit.get_tools()) == 5


@pytest.mark.unit
def test_add_tool(github_toolkit):
    tool = AdditionTool()
    github_toolkit.add_tool(tool)
    assert len(github_toolkit.get_tools()) == 6


@pytest.mark.parametrize(
    "action, kwargs, method_called",
    [
        ("create_repo", {"repo_name": "test-repo"}, "create_repo"),
        ("delete_repo", {"repo_name": "test-repo"}, "delete_repo"),
        ("get_repo", {"repo_name": "test-repo"}, "get_repo"),
        ("list_repos", {}, "list_repos"),
        ("update_repo", {"repo_name": "test-repo"}, "update_repo"),
        ("invalid_action", {}, None),
    ],
)
@pytest.mark.unit
@patch("swarmauri_tool_github.GithubRepoTool.Github")
def test_call_github_repo_tool(
    mock_github, github_toolkit, action, kwargs, method_called
):
    expected_keys = {action}
    tool_name = "GithubRepoTool"

    mock_github.return_value = MagicMock()

    if method_called is not None:
        with patch.object(
            GithubRepoTool,
            method_called,
            return_value="performed a test action successfully",
        ) as mock_method:
            result = github_toolkit.get_tool_by_name(tool_name)(action=action, **kwargs)

            mock_method.assert_called_once_with(**kwargs)

            assert isinstance(
                result, dict
            ), f"Expected dict, but got {type(result).__name__}"
            assert expected_keys.issubset(
                result.keys()
            ), f"Expected keys {expected_keys} but got {result.keys()}"
            assert isinstance(
                result.get(action), str
            ), f"Expected str, but got {type(result.get(action)).__name__}"
            assert result == {f"{action}": "performed a test action successfully"}
    else:
        with pytest.raises(ValueError, match=f"Action '{action}' is not supported."):
            github_toolkit.get_tool_by_name(tool_name)(action=action, **kwargs)
