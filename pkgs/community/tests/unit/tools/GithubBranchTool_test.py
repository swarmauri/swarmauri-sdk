import os
from unittest.mock import MagicMock, patch
from dotenv import load_dotenv

import pytest
from swarmauri_community.tools.concrete.GithubBranchTool import (
    GithubBranchTool as Tool,
)

load_dotenv()


@pytest.mark.unit
@pytest.mark.skipif(
    not os.getenv("GITHUBTOOL_TEST_TOKEN"),
    reason="Skipping due to environment variable not set",
)
def test_ubc_resource():
    token = os.getenv("GITHUBTOOL_TEST_TOKEN")
    tool = Tool(token=token)
    assert tool.resource == "Tool"


@pytest.mark.unit
@pytest.mark.skipif(
    not os.getenv("GITHUBTOOL_TEST_TOKEN"),
    reason="Skipping due to environment variable not set",
)
def test_ubc_type():
    token = os.getenv("GITHUBTOOL_TEST_TOKEN")
    assert Tool(token=token).type == "GithubBranchTool"


@pytest.mark.unit
@pytest.mark.skipif(
    not os.getenv("GITHUBTOOL_TEST_TOKEN"),
    reason="Skipping due to environment variable not set",
)
def test_initialization():
    token = os.getenv("GITHUBTOOL_TEST_TOKEN")
    tool = Tool(token=token)
    assert type(tool.id) == str


@pytest.mark.unit
@pytest.mark.skipif(
    not os.getenv("GITHUBTOOL_TEST_TOKEN"),
    reason="Skipping due to environment variable not set",
)
def test_serialization():
    token = os.getenv("GITHUBTOOL_TEST_TOKEN")
    tool = Tool(token=token)
    assert tool.id == Tool.model_validate_json(tool.model_dump_json()).id


@pytest.mark.parametrize(
    "action, kwargs, method_called",
    [
        (
            "create_branch",
            {
                "repo_name": "test-repo",
                "branch_name": "new-branch",
                "source_branch": "main",
            },
            "create_branch",
        ),
        (
            "delete_branch",
            {"repo_name": "test-repo", "branch_name": "new-branch"},
            "delete_branch",
        ),
        ("list_branches", {"repo_name": "test-repo"}, "list_branches"),
        ("get_branch", {"repo_name": "test-repo", "branch_name": "main"}, "get_branch"),
        # Invalid action
        ("invalid_action", {}, None),
    ],
)
@pytest.mark.skipif(
    not os.getenv("GITHUBTOOL_TEST_TOKEN"),
    reason="Skipping due to environment variable not set",
)
@pytest.mark.unit
@patch("swarmauri_community.tools.concrete.GithubTool.Github")
def test_call(mock_github, action, kwargs, method_called):
    expected_keys = {action}
    token = os.getenv("GITHUBTOOL_TEST_TOKEN")
    tool = Tool(token=token)

    mock_github.return_value = MagicMock()

    if method_called is not None:
        with patch.object(
            Tool,
            method_called,
            return_value="performed a test action successfully",
        ) as mock_method:
            result = tool(action=action, **kwargs)

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
            tool(action=action, **kwargs)
