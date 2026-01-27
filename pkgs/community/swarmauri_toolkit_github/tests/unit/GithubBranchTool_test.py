import os
from unittest.mock import MagicMock, patch
from dotenv import load_dotenv

import pytest
from swarmauri_toolkit_github.GithubBranchTool import (
    GithubBranchTool as Tool,
)

# Load environment variables from the .env file
load_dotenv()


# Fixture for retrieving GitHub api_token and skipping tests if not available
@pytest.fixture(scope="module")
def github_api_token():
    api_token = os.getenv("GITHUBTOOL_TEST_TOKEN")
    if not api_token:
        pytest.skip("Skipping due to GITHUBTOOL_TEST_TOKEN not set")
    return api_token


# Fixture for initializing the GithubBranchTool
@pytest.fixture(scope="module")
def github_branch_tool(github_api_token):
    return Tool(api_token=github_api_token)


@pytest.mark.unit
def test_ubc_resource(github_branch_tool):
    assert github_branch_tool.resource == "Tool"


@pytest.mark.unit
def test_ubc_type(github_branch_tool):
    assert github_branch_tool.type == "GithubBranchTool"


@pytest.mark.unit
def test_initialization(github_branch_tool):
    assert type(github_branch_tool.id) is str


@pytest.mark.unit
def test_serialization(github_branch_tool):
    serialized_data = github_branch_tool.model_dump_json()
    deserialized_tool = Tool.model_validate_json(serialized_data)
    assert github_branch_tool.id == deserialized_tool.id


@pytest.mark.parametrize(
    "action, kwargs, method_called",
    [
        (
            "create_branch",
            {
                "repo_name": "test-repo",
                "branch_name": "new-branch",
                "source_branch": "master",
            },
            "create_branch",
        ),
        (
            "delete_branch",
            {"repo_name": "test-repo", "branch_name": "new-branch"},
            "delete_branch",
        ),
        ("list_branches", {"repo_name": "test-repo"}, "list_branches"),
        (
            "get_branch",
            {"repo_name": "test-repo", "branch_name": "master"},
            "get_branch",
        ),
        # Invalid action
        ("invalid_action", {}, None),
    ],
)
@pytest.mark.unit
@patch("swarmauri_toolkit_github.GithubBranchTool.Github")
def test_call(mock_github, github_branch_tool, action, kwargs, method_called):
    expected_keys = {action}

    # Mock the GitHub object
    mock_github.return_value = MagicMock()

    if method_called is not None:
        with patch.object(
            Tool,
            method_called,
            return_value="performed a test action successfully",
        ) as mock_method:
            result = github_branch_tool(action=action, **kwargs)

            # Verify the method is called with the correct arguments
            mock_method.assert_called_once_with(**kwargs)

            # Check the result
            assert isinstance(result, dict), (
                f"Expected dict, but got {type(result).__name__}"
            )
            assert expected_keys.issubset(result.keys()), (
                f"Expected keys {expected_keys} but got {result.keys()}"
            )
            assert isinstance(result.get(action), str), (
                f"Expected str, but got {type(result.get(action)).__name__}"
            )
            assert result == {f"{action}": "performed a test action successfully"}
    else:
        # If an invalid action is provided, it should raise a ValueError
        with pytest.raises(ValueError, match=f"Action '{action}' is not supported."):
            github_branch_tool(action=action, **kwargs)
