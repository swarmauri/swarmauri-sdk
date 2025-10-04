import os
from unittest.mock import MagicMock, patch
from dotenv import load_dotenv

import pytest
from swarmauri_toolkit_github.GithubCommitTool import (
    GithubCommitTool as Tool,
)

load_dotenv()


# Fixture for retrieving GitHub api_token and skipping tests if not available
@pytest.fixture(scope="module")
def github_api_token():
    api_token = os.getenv("GITHUBTOOL_TEST_TOKEN")
    if not api_token:
        pytest.skip("Skipping due to GITHUBTOOL_TEST_TOKEN not set")
    return api_token


# Fixture for initializing the GithubCommitTool
@pytest.fixture(scope="module")
def github_commit_tool(github_api_token):
    return Tool(api_token=github_api_token)


@pytest.mark.unit
def test_ubc_resource(github_commit_tool):
    assert github_commit_tool.resource == "Tool"


@pytest.mark.unit
def test_ubc_type(github_commit_tool):
    assert github_commit_tool.type == "GithubCommitTool"


@pytest.mark.unit
def test_initialization(github_commit_tool):
    assert type(github_commit_tool.id) is str


@pytest.mark.unit
def test_serialization(github_commit_tool):
    assert (
        github_commit_tool.id
        == Tool.model_validate_json(github_commit_tool.model_dump_json()).id
    )


@pytest.mark.parametrize(
    "action, kwargs, method_called",
    [
        # Valid cases for repo management
        (
            "create_commit",
            {
                "repo_name": "test-repo",
                "file_path": "path/to/file.txt",
                "message": "Test Commit",
                "content": "File content",
                "branch": "master",
            },
            "create_commit",
        ),
        ("list_commits", {"repo_name": "test-repo"}, "list_commits"),
        ("get_commit", {"repo_name": "test-repo", "sha": "abcdef"}, "get_commit"),
        (
            "compare_commits",
            {"repo_name": "test-repo", "base": "master", "head": "feature"},
            "compare_commits",
        ),
        # Invalid action
        ("invalid_action", {}, None),
    ],
)
@pytest.mark.unit
@patch("swarmauri_toolkit_github.GithubCommitTool.Github")
def test_call(mock_github, github_commit_tool, action, kwargs, method_called):
    expected_keys = {action}

    mock_github.return_value = MagicMock()

    if method_called is not None:
        with patch.object(
            Tool,
            method_called,
            return_value="performed a test action successfully",
        ) as mock_method:
            result = github_commit_tool(action=action, **kwargs)

            mock_method.assert_called_once_with(**kwargs)

            assert isinstance(result, dict), (
                f"Expected dict, but got {type(result).__name__}"
            )
            assert expected_keys.issubset(result.keys()), (
                f"Expected keys {expected_keys} but got {result.keys()}"
            )
            assert isinstance(result.get(action), str), (
                f"Expected int, but got {type(result.get(action)).__name__}"
            )
            assert result == {f"{action}": "performed a test action successfully"}
    else:
        with pytest.raises(ValueError, match=f"Action '{action}' is not supported."):
            github_commit_tool(action=action, **kwargs)
