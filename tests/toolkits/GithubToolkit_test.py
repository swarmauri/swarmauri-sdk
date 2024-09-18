import json
import os
from unittest.mock import patch, MagicMock
import pytest
import logging

from sympy.ntheory.primetest import proth_test

from swarmauri.standard.tools.concrete.AdditionTool import AdditionTool
from swarmauri.community.tools.concrete.GithubRepoTool import GithubRepoTool
from swarmauri.community.toolkits.concrete.GithubToolkit import GithubToolkit as Toolkit
from dotenv import load_dotenv

load_dotenv()

token = os.getenv("GITHUBTOOL_TEST_TOKEN")


@pytest.mark.unit
def test_ubc_resource():
    toolkit = Toolkit(token=token)
    assert toolkit.resource == "GithubToolkit"


@pytest.mark.unit
def test_ubc_type():
    toolkit = Toolkit(token=token)
    assert toolkit.type == "GithubToolkit"


@pytest.mark.unit
def test_serialization():
    toolkit = Toolkit(token=token)

    serialized_data = toolkit.model_dump_json()
    logging.info(serialized_data)

    deserialized_toolkit = Toolkit.model_validate_json(serialized_data)

    assert toolkit.id == deserialized_toolkit.id
    # assert (
    #     toolkit.tools["GithubPRTool"].id
    #     == deserialized_toolkit.tools["GithubPRTool"].id
    # )
    # assert toolkit == deserialized_toolkit


@pytest.mark.unit
def test_tool_count():
    toolkit = Toolkit(token=token)
    assert len(toolkit.get_tools()) == 3


@pytest.mark.unit
def test_add_tool():
    toolkit = Toolkit(token=token)
    tool = AdditionTool()
    toolkit.add_tool(tool)
    assert len(toolkit.get_tools()) == 4


@pytest.mark.parametrize(
    "action, kwargs, method_called",
    [
        # Valid cases for repo management
        ("create_repo", {"repo_name": "test-repo"}, "create_repo"),
        ("delete_repo", {"repo_name": "test-repo"}, "delete_repo"),
        ("get_repo", {"repo_name": "test-repo"}, "get_repo"),
        ("list_repos", {}, "list_repos"),
        ("update_repo", {"repo_name": "test-repo"}, "update_repo"),
        # Invalid action
        ("invalid_action", {}, None),
    ],
)
@pytest.mark.unit
@patch("swarmauri.community.tools.concrete.GithubRepoTool.Github")
def test_call_github_repo_tool(mock_github, action, kwargs, method_called):
    expected_keys = {action}
    toolkit = Toolkit(token=token)
    tool_name = "GithubRepoTool"

    mock_github.return_value = MagicMock()

    if method_called is not None:
        with patch.object(
            GithubRepoTool,
            method_called,
            return_value="performed a test action successfully",
        ) as mock_method:
            result = toolkit.get_tool_by_name(tool_name)(action=action, **kwargs)

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
            toolkit.get_tool_by_name(tool_name)(action=action, **kwargs)
