import os
from unittest.mock import MagicMock, patch

import pytest
from swarmauri.community.tools.concrete.GithubTool import GithubTool as Tool


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
    assert Tool(token=token).type == "GithubTool"


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
    "action, kwargs, method_called, expected_result",
    [
        # Valid cases for repo management
        (
            "create_repo",
            {"repo_name": "test-repo"},
            "create_repo",
            {"create_repo": "test action"},
        ),
        (
            "delete_repo",
            {"repo_name": "test-repo"},
            "delete_repo",
            {"delete_repo": "test action"},
        ),
        (
            "get_repo",
            {"repo_name": "test-repo"},
            "get_repo",
            {"get_repo": "test action"},
        ),
        ("list_repos", {}, "list_repos", {"list_repos": "test action"}),
        # Valid cases for issue management
        (
            "create_issue",
            {"repo_name": "test-repo", "title": "Test Issue"},
            "create_issue",
            {"create_issue": "test action"},
        ),
        (
            "close_issue",
            {"repo_name": "test-repo", "issue_number": 1},
            "close_issue",
            {"close_issue": "test action"},
        ),
        # Invalid action
        ("invalid_action", {}, None, None),
    ],
)
@pytest.mark.skipif(
    not os.getenv("GITHUBTOOL_TEST_TOKEN"),
    reason="Skipping due to environment variable not set",
)
@pytest.mark.unit
@patch("swarmauri.community.tools.concrete.GithubTool.Github")
def test_call(mock_github, action, kwargs, method_called, expected_result):
    token = os.getenv("GITHUBTOOL_TEST_TOKEN")

    # Initialize the tool object
    tool = Tool(token=token)

    # Mock the Github API calls
    mock_github.return_value = MagicMock()

    if method_called is not None:
        # Use patch.object to mock the specific method within the Tool instance
        with patch.object(
            tool, method_called, return_value="test action"
        ) as method_mock:
            # Call the __call__ method
            result = tool(action=action, **kwargs)

            # Assert that the correct method was called with the correct arguments
            method_mock.assert_called_once_with(**kwargs)

            # Assert that the result matches the expected output
            assert result == expected_result

    else:
        # Test the case when an invalid action is provided
        with pytest.raises(ValueError, match=f"Action '{action}' is not supported."):
            tool(action=action, **kwargs)
