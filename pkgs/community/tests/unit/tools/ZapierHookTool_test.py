from unittest.mock import patch
import json

import pytest
import requests
from swarmauri_community.tools.concrete.ZapierHookTool import (
    ZapierHookTool as Tool,
)


@pytest.mark.unit
def test_ubc_resource():
    tool = Tool(zap_url="dummy_zap_id")
    assert tool.resource == "Tool"


@pytest.mark.unit
def test_ubc_type():
    assert Tool(zap_url="dummy_zap_id").type == "ZapierHookTool"


@pytest.mark.unit
def test_initialization():
    tool = Tool(zap_url="dummy_zap_id")
    assert type(tool.id) == str


@pytest.mark.unit
def test_serialization():
    tool = Tool(zap_url="dummy_zap_id")
    assert tool.id == Tool.model_validate_json(tool.model_dump_json()).id


@pytest.mark.parametrize(
    "payload, response_status, response_json, expected_output, should_raise",
    [
        (
            '{"key": "value"}',
            200,
            {"status": "success"},
            {"status": "success"},
            False,  # Add the missing value for 'should_raise'
        ),  # Valid case: successful zap execution
        (
            '{"key": "value"}',
            404,
            None,
            True,
            True,  # Add the missing value for 'should_raise'
        ),  # Invalid case: 404 Not Found error
        (
            '{"key": "value"}',
            500,
            None,
            True,
            True,  # Add the missing value for 'should_raise'
        ),  # Invalid case: 500 Internal Server Error
    ],
)
@patch("requests.post")
@pytest.mark.unit
def test_call(
    mock_post,
    payload,
    response_status,
    response_json,
    expected_output,
    should_raise,
):
    tool = Tool(zap_url="dummy_zap_url")
    mock_response = mock_post.return_value
    mock_response.status_code = response_status
    if response_json is not None:
        mock_response.json.return_value = response_json
    else:
        mock_response.json.side_effect = ValueError("No JSON response")

    # Set the side effect to raise HTTPError for non-200 responses
    if response_status != 200:
        mock_response.raise_for_status.side_effect = requests.HTTPError()

    if should_raise:
        with pytest.raises(requests.HTTPError):
            tool(payload)
    else:
        result = tool(payload)

        # assert that it is a dict and contains the expected keys
        assert isinstance(result, dict)
        assert "zap_response" in result

        # assert that the output is as expected
        output = json.loads(result["zap_response"])
        assert output == expected_output

    mock_post.assert_called_with(
        "dummy_zap_url",
        json={"data": payload},
    )
