import os
from unittest.mock import MagicMock, patch
from dotenv import load_dotenv

import pytest
from swarmauri_tool_communitygithub.GithubPRTool import (
    GithubPRTool as Tool,
)

load_dotenv()


# Fixture for retrieving GitHub token and skipping tests if not available
@pytest.fixture(scope="module")
def github_token():
    token = os.getenv("GITHUBTOOL_TEST_TOKEN")
    if not token:
        pytest.skip("Skipping due to GITHUBTOOL_TEST_TOKEN not set")
    return token


# Fixture for initializing the GithubPRTool
@pytest.fixture(scope="module")
def github_pr_tool(github_token):
    return Tool(token=github_token)


@pytest.mark.unit
def test_ubc_resource(github_pr_tool):
    assert github_pr_tool.resource == "Tool"


@pytest.mark.unit
def test_ubc_type(github_pr_tool):
    assert github_pr_tool.type == "GithubPRTool"


@pytest.mark.unit
def test_initialization(github_pr_tool):
    assert type(github_pr_tool.id) == str


@pytest.mark.unit
def test_serialization(github_pr_tool):
    assert (
        github_pr_tool.id
        == Tool.model_validate_json(github_pr_tool.model_dump_json()).id
    )


@pytest.mark.parametrize(
    "action, kwargs, method_called",
    [
        # Valid cases for repo management
        ("create_pull", {"repo_name": "test-repo", "title": "Test PR"}, "create_pull"),
        ("merge_pull", {"repo_name": "test-repo", "pull_number": 1}, "merge_pull"),
        ("close_pull", {"repo_name": "test-repo", "pull_number": 1}, "close_pull"),
        ("list_pulls", {"repo_name": "test-repo"}, "list_pulls"),
        ("get_pull", {"repo_name": "test-repo", "pull_number": 1}, "get_pull"),
        # Invalid action
        ("invalid_action", {}, None),
    ],
)
@pytest.mark.unit
@patch("swarmauri_community.tools.concrete.GithubPRTool.Github")
def test_call(mock_github, github_pr_tool, action, kwargs, method_called):
    expected_keys = {action}

    mock_github.return_value = MagicMock()

    if method_called is not None:
        with patch.object(
            Tool,
            method_called,
            return_value="performed a test action successfully",
        ) as mock_method:
            result = github_pr_tool(action=action, **kwargs)

            mock_method.assert_called_once_with(**kwargs)

            assert isinstance(
                result, dict
            ), f"Expected dict, but got {type(result).__name__}"
            assert expected_keys.issubset(
                result.keys()
            ), f"Expected keys {expected_keys} but got {result.keys()}"
            assert isinstance(
                result.get(action), str
            ), f"Expected int, but got {type(result.get(action)).__name__}"
            assert result == {f"{action}": "performed a test action successfully"}
    else:
        with pytest.raises(ValueError, match=f"Action '{action}' is not supported."):
            github_pr_tool(action=action, **kwargs)
