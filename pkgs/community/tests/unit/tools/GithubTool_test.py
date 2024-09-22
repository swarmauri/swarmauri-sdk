import os
from unittest.mock import MagicMock, patch
from dotenv import load_dotenv

import pytest
from swarmauri_community.community.tools.concrete.GithubTool import GithubTool as Tool

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
    "action, kwargs, method_called",
    [
        # Valid cases for repo management
        ("create_repo", {"repo_name": "test-repo"}, "create_repo"),
        ("delete_repo", {"repo_name": "test-repo"}, "delete_repo"),
        ("get_repo", {"repo_name": "test-repo"}, "get_repo"),
        ("list_repos", {}, "list_repos"),
        ("update_repo", {"repo_name": "test-repo"}, "update_repo"),
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
        ("create_pull", {"repo_name": "test-repo", "title": "Test PR"}, "create_pull"),
        ("merge_pull", {"repo_name": "test-repo", "pull_number": 1}, "merge_pull"),
        ("close_pull", {"repo_name": "test-repo", "pull_number": 1}, "close_pull"),
        ("list_pulls", {"repo_name": "test-repo"}, "list_pulls"),
        ("get_pull", {"repo_name": "test-repo", "pull_number": 1}, "get_pull"),
        (
            "create_commit",
            {"repo_name": "test-repo", "message": "Test Commit"},
            "create_commit",
        ),
        ("list_commits", {"repo_name": "test-repo"}, "list_commits"),
        (
            "get_commit",
            {"repo_name": "test-repo", "commit_sha": "abcdef"},
            "get_commit",
        ),
        (
            "compare_commits",
            {"repo_name": "test-repo", "base": "main", "head": "feature"},
            "compare_commits",
        ),
        (
            "create_branch",
            {"repo_name": "test-repo", "branch_name": "new-branch"},
            "create_branch",
        ),
        (
            "delete_branch",
            {"repo_name": "test-repo", "branch_name": "new-branch"},
            "delete_branch",
        ),
        ("list_branches", {"repo_name": "test-repo"}, "list_branches"),
        ("get_branch", {"repo_name": "test-repo", "branch_name": "main"}, "get_branch"),
        (
            "add_collaborator",
            {"repo_name": "test-repo", "username": "collaborator"},
            "add_collaborator",
        ),
        (
            "remove_collaborator",
            {"repo_name": "test-repo", "username": "collaborator"},
            "remove_collaborator",
        ),
        ("list_collaborators", {"repo_name": "test-repo"}, "list_collaborators"),
        (
            "check_collaborator",
            {"repo_name": "test-repo", "username": "collaborator"},
            "check_collaborator",
        ),
        (
            "create_milestone",
            {"repo_name": "test-repo", "title": "Milestone 1"},
            "create_milestone",
        ),
        (
            "close_milestone",
            {"repo_name": "test-repo", "milestone_number": 1},
            "close_milestone",
        ),
        (
            "update_milestone",
            {
                "repo_name": "test-repo",
                "milestone_number": 1,
                "title": "Updated Milestone",
            },
            "update_milestone",
        ),
        ("list_milestones", {"repo_name": "test-repo"}, "list_milestones"),
        (
            "get_milestone",
            {"repo_name": "test-repo", "milestone_number": 1},
            "get_milestone",
        ),
        (
            "create_label",
            {"repo_name": "test-repo", "name": "bug", "color": "f29513"},
            "create_label",
        ),
        ("delete_label", {"repo_name": "test-repo", "name": "bug"}, "delete_label"),
        (
            "update_label",
            {"repo_name": "test-repo", "name": "bug", "color": "f29513"},
            "update_label",
        ),
        ("list_labels", {"repo_name": "test-repo"}, "list_labels"),
        ("get_label", {"repo_name": "test-repo", "name": "bug"}, "get_label"),
        (
            "create_webhook",
            {"repo_name": "test-repo", "config": {"url": "http://example.com"}},
            "create_webhook",
        ),
        ("delete_webhook", {"repo_name": "test-repo", "hook_id": 1}, "delete_webhook"),
        ("list_webhooks", {"repo_name": "test-repo"}, "list_webhooks"),
        ("get_webhook", {"repo_name": "test-repo", "hook_id": 1}, "get_webhook"),
        (
            "create_gist",
            {
                "description": "Test Gist",
                "files": {"file1.txt": {"content": "Hello World"}},
            },
            "create_gist",
        ),
        ("delete_gist", {"gist_id": "12345"}, "delete_gist"),
        (
            "update_gist",
            {"gist_id": "12345", "description": "Updated Gist"},
            "update_gist",
        ),
        ("list_gists", {"username": "test-user"}, "list_gists"),
        ("get_gist", {"gist_id": "12345"}, "get_gist"),
        # Invalid action
        ("invalid_action", {}, None),
    ],
)
@pytest.mark.skipif(
    not os.getenv("GITHUBTOOL_TEST_TOKEN"),
    reason="Skipping due to environment variable not set",
)
@pytest.mark.unit
@patch("swarmauri_community.community.tools.concrete.GithubTool.Github")
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
