import os
from unittest.mock import MagicMock, patch

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

@pytest.mark.parametrize("action, kwargs, method_called", [
    # Valid cases for repo management
    ("create_repo", {"repo_name": "test-repo"}, "create_repo"),
    ("delete_repo", {"repo_name": "test-repo"}, "delete_repo"),
    ("get_repo", {"repo_name": "test-repo"}, "get_repo"),
    ("list_repos", {}, "list_repos"),

    # Valid cases for issue management
    ("create_issue", {"repo_name": "test-repo", "title": "Test Issue"}, "create_issue"),
    ("close_issue", {"repo_name": "test-repo", "issue_number": 1}, "close_issue"),

    # Invalid action
    ("invalid_action", {}, None),
])
@pytest.mark.skipif(not os.getenv('GITHUBTOOL_TEST_TOKEN'), reason="Skipping due to environment variable not set")
@patch('swarmauri.standard.tools.concrete.GithubTool.Github')
def test_call(mock_github, action, kwargs, method_called):
    token = os.getenv("GITHUBTOOL_TEST_TOKEN")
    tool = Tool(token=token)

    mock_github.return_value = MagicMock()

    if method_called is not None:
        with patch.object(tool, method_called, return_value="Success") as mock_method:
            result = tool(action=action, **kwargs)

            mock_method.assert_called_once_with(**kwargs)
            assert result == "Success"

    else:
        with pytest.raises(ValueError, match=f"Action '{action}' is not supported."):
            tool(action=action, **kwargs)
