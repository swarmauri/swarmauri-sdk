from unittest.mock import patch

import pytest
import requests
from swarmauri.community.tools.concrete.ZapierHookTool import ZapierHookTool as Tool

headers = {
        "Authorization": "Bearer dummy_token",
        "Content-Type": "application/json"
    }

@pytest.mark.unit
def test_ubc_resource():
    tool = Tool(auth_token="dummy_token", zap_id="dummy_zap_id", headers=headers)
    assert tool.resource == 'Tool'

@pytest.mark.unit
def test_ubc_type():
    assert Tool(auth_token="dummy_token", zap_id="dummy_zap_id", headers=headers).type == 'ZapierHookTool'

@pytest.mark.unit
def test_initialization():
    tool = Tool(auth_token="dummy_token", zap_id="dummy_zap_id", headers=headers)
    assert type(tool.id) == str

@pytest.mark.unit
def test_serialization():
    tool = Tool(auth_token="dummy_token", zap_id="dummy_zap_id", headers=headers)
    assert tool.id == Tool.model_validate_json(tool.model_dump_json()).id

@pytest.mark.parametrize("payload, response_status, response_json, expected_output, should_raise", [
    ("{'key': 'value'}", 200, {"status": "success"}, '{"status": "success"}', False), # Valid case: successful zap execution
    ("{'key': 'value'}", 404, None, None, True),  # Invalid case: 404 Not Found error
    ("{'key': 'value'}", 500, None, None, True),  # Invalid case: 500 Internal Server Error
])
@patch('requests.post')
@pytest.mark.unit
def test_call(mock_post, payload, response_status, response_json, expected_output, should_raise):
    tool = Tool(auth_token="dummy_token", zap_id="dummy_zap_id", headers=headers)
    mock_response = mock_post.return_value
    mock_response.status_code = response_status
    if response_json is not None:
        mock_response.json.return_value = response_json
    else:
        mock_response.json.side_effect = ValueError("No JSON response")

    if should_raise:
        with pytest.raises(requests.HTTPError):
            tool(payload)
    else:
        result = tool(payload)
        assert result == expected_output

    mock_post.assert_called_with(
        f'https://hooks.zapier.com/hooks/catch/dummy_zap_id/',
        headers=headers,
        json={"data": payload}
    )
    assert result["num_characters"] == 26
    assert result["num_words"] == 7
    assert result["num_sentences"] == 1
