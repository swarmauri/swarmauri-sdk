import os
from unittest.mock import patch, MagicMock

import pytest
from swarmauri.community.tools.concrete.GithubTool import GithubTool as Tool

@pytest.mark.unit
@pytest.mark.skipif(not os.getenv('GITHUBTOOL_TEST_TOKEN'), reason="Skipping due to environment variable not set")
def test_ubc_resource():
    token = os.getenv("GITHUBTOOL_TEST_TOKEN")
    tool = Tool(token=token)
    assert tool.resource == 'Tool'

@pytest.mark.unit
@pytest.mark.skipif(not os.getenv('GITHUBTOOL_TEST_TOKEN'), reason="Skipping due to environment variable not set")
def test_ubc_type():
    token = os.getenv("GITHUBTOOL_TEST_TOKEN")
    assert Tool(token=token).type == 'GithubTool'

@pytest.mark.unit
@pytest.mark.skipif(not os.getenv('GITHUBTOOL_TEST_TOKEN'), reason="Skipping due to environment variable not set")
def test_initialization():
    token = os.getenv("GITHUBTOOL_TEST_TOKEN")
    tool = Tool(token=token)
    assert type(tool.id) == str

@pytest.mark.unit
@pytest.mark.skipif(not os.getenv('GITHUBTOOL_TEST_TOKEN'), reason="Skipping due to environment variable not set")
def test_serialization():
    token = os.getenv("GITHUBTOOL_TEST_TOKEN")
    tool = Tool(token=token)
    assert tool.id == Tool.model_validate_json(tool.model_dump_json()).id

@pytest.mark.parametrize("action, kwargs, expected", [
    ("create_repo", {"repo_name": "test_repo", "private": False}, "Repository 'test_repo' created successfully."),
    ("delete_repo", {"repo_name": "test_repo"}, "Repository 'test_repo' deleted successfully."),
    ("get_repo", {"repo_name": "test_repo"}, "Repository: test_repo"),
    ("list_repos", {}, ["test_repo"]),
    ("update_repo", {"repo_name": "test_repo", "description": "Updated description"},
     "Repository 'test_repo' updated successfully."),
    ("create_issue", {"repo_name": "test_repo", "title": "New Issue", "body": "Issue body"},
     "Issue 'New Issue' created successfully."),
    ("close_issue", {"repo_name": "test_repo", "issue_number": 1}, "Issue '1' closed successfully."),
    ("update_issue", {"repo_name": "test_repo", "issue_number": 1, "title": "Updated Issue"},
     "Issue '1' updated successfully."),
    ("list_issues", {"repo_name": "test_repo"}, ["Issue 1"]),
    ("get_issue", {"repo_name": "test_repo", "issue_number": 1}, "Issue #1: Issue Title"),
    ("create_pull", {"repo_name": "test_repo", "title": "New PR", "head": "feature-branch", "base": "main"},
     "Pull request 'New PR' created successfully."),
    ("merge_pull", {"repo_name": "test_repo", "pull_number": 1}, "Pull request '1' merged successfully."),
    ("close_pull", {"repo_name": "test_repo", "pull_number": 1}, "Pull request '1' closed successfully."),
    ("list_pulls", {"repo_name": "test_repo"}, ["PR 1"]),
    ("get_pull", {"repo_name": "test_repo", "pull_number": 1}, "Pull Request #1: PR Title"),
    ("create_commit",
     {"repo_name": "test_repo", "path": "README.md", "message": "Initial commit", "content": "Hello, World!",
      "branch": "main"}, "Commit created successfully at README.md."),
    ("list_commits", {"repo_name": "test_repo"}, ["Initial commit"]),
    ("get_commit", {"repo_name": "test_repo", "sha": "abc123"}, "Commit abc123: Initial commit"),
    ("compare_commits", {"repo_name": "test_repo", "base": "main", "head": "feature-branch"},
     "Comparison from main to feature-branch:"),
    ("create_branch", {"repo_name": "test_repo", "branch_name": "new-branch", "source": "main"},
     "Branch 'new-branch' created successfully."),
    ("delete_branch", {"repo_name": "test_repo", "branch_name": "new-branch"},
     "Branch 'new-branch' deleted successfully."),
    ("list_branches", {"repo_name": "test_repo"}, ["main", "new-branch"]),
    ("get_branch", {"repo_name": "test_repo", "branch_name": "main"}, "Branch main: abc123"),
    ("add_collaborator", {"repo_name": "test_repo", "username": "collaborator", "permission": "push"},
     "Collaborator 'collaborator' added successfully with 'push' permission."),
    ("remove_collaborator", {"repo_name": "test_repo", "username": "collaborator"},
     "Collaborator 'collaborator' removed successfully."),
    ("list_collaborators", {"repo_name": "test_repo"}, ["collaborator"]),
    ("check_collaborator", {"repo_name": "test_repo", "username": "collaborator"},
     "User 'collaborator' is a collaborator."),
    ("create_milestone", {"repo_name": "test_repo", "title": "v1.0", "description": "Initial release", "state": "open"},
     "Milestone 'v1.0' created successfully."),
    ("close_milestone", {"repo_name": "test_repo", "milestone_number": 1}, "Milestone 'v1.0' closed successfully."),
    ("update_milestone", {"repo_name": "test_repo", "milestone_number": 1, "title": "v1.1"},
     "Milestone 'v1.1' updated successfully."),
    ("list_milestones", {"repo_name": "test_repo"}, ["v1.0"]),
    ("get_milestone", {"repo_name": "test_repo", "milestone_number": 1}, "Milestone 'v1.0': Description"),
    ("create_label", {"repo_name": "test_repo", "name": "bug", "color": "f29513"}, "Label 'bug' created successfully."),
    ("delete_label", {"repo_name": "test_repo", "name": "bug"}, "Label 'bug' deleted successfully."),
    ("update_label", {"repo_name": "test_repo", "name": "bug", "color": "d73a4a"}, "Label 'bug' updated successfully."),
    ("list_labels", {"repo_name": "test_repo"}, ["bug"]),
    ("get_label", {"repo_name": "test_repo", "name": "bug"}, "Label 'bug': Description"),
    ("create_webhook", {"repo_name": "test_repo", "config": {"url": "https://example.com/webhook"}, "events": ["push"]},
     "Webhook created successfully."),
    ("delete_webhook", {"repo_name": "test_repo", "webhook_id": 1}, "Webhook '1' deleted successfully."),
    ("list_webhooks", {"repo_name": "test_repo"}, ["Webhook 1"]),
    ("get_webhook", {"repo_name": "test_repo", "webhook_id": 1}, "Webhook '1': Config"),
    ("create_gist", {"description": "Example gist", "files": {"file1.txt": {"content": "Hello World!"}}},
     "Gist created successfully."),
    ("delete_gist", {"gist_id": "gist123"}, "Gist 'gist123' deleted successfully."),
    ("update_gist", {"gist_id": "gist123", "files": {"file1.txt": {"content": "Updated content"}}},
     "Gist 'gist123' updated successfully."),
    ("list_gists", {}, ["Gist 1"]),
    ("get_gist", {"gist_id": "gist123"}, "Gist 'gist123': Description"),
])

@pytest.mark.skipif(not os.getenv('GITHUBTOOL_TEST_TOKEN'), reason="Skipping due to environment variable not set")
@pytest.mark.unit
def test_call(action, kwargs, expected):
    token = os.getenv("GITHUBTOOL_TEST_TOKEN")
    tool = Tool(token=token)

    result = tool(action, **kwargs)

    assert result == expected
