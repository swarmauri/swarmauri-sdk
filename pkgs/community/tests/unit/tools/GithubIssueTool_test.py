import os
from unittest.mock import MagicMock, patch
from dotenv import load_dotenv

import pytest
from swarmauri_community.tools.concrete.GithubIssueTool import (
    GithubIssueTool as Tool,
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
    assert Tool(token=token).type == "GithubIssueTool"


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
            "create_issue",
            {"repo_name": "test-repo", "title": "Test Issue"},
            "create_issue",
        ),
        ("close_issue", {"repo_name": "test-repo", "issue_number": 1}, "close_issue"),
        (
            "update_issue",
            {"repo_name": "test-repo", "issue_number": 1, "title": "Updated Issue"},
            "update_issue",
        ),
        ("list_issues", {"repo_name": "test-repo"}, "list_issues"),
        ("get_issue", {"repo_name": "test-repo", "issue_number": 1}, "get_issue"),
        # Invalid action
        ("invalid_action", {}, None),
    ],
)
@pytest.mark.skipif(
    not os.getenv("GITHUBTOOL_TEST_TOKEN"),
    reason="Skipping due to environment variable not set",
)
@pytest.mark.unit
@patch("swarmauri_community.tools.concrete.GithubIssueTool.Github")
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
