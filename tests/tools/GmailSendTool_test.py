from unittest.mock import patch, MagicMock

import pytest
from swarmauri.community.tools.concrete.GmailSendTool import GmailSendTool as Tool

@pytest.mark.unit
def test_ubc_resource():
    tool = Tool(credentials_path='fake_credentials.json', sender_email='test@example.com')
    assert tool.resource == 'Tool'

@pytest.mark.unit
def test_ubc_type():
    assert Tool(credentials_path='fake_credentials.json', sender_email='test@example.com').type == 'GmailSendTool'

@pytest.mark.unit
def test_initialization():
    tool = Tool(credentials_path='fake_credentials.json', sender_email='test@example.com')
    assert type(tool.id) == str

@pytest.mark.unit
def test_serialization():
    tool = Tool(credentials_path='fake_credentials.json', sender_email='test@example.com')
    assert tool.id == Tool.model_validate_json(tool.model_dump_json()).id


@pytest.mark.parametrize("send_method_side_effect, expected_result", [
    # Success scenario
    (None, "Email sent successfully to recipient@example.com"),
    # Failure scenario
    (Exception("API Error"), "An error occurred in sending the email: API Error"),
])
@pytest.mark.unit
@patch.object(Tool, 'authenticate')
@patch.object(Tool, 'create_message')
@patch('googleapiclient.discovery.build')
def test_call(mock_build, mock_create_message, mock_authenticate, send_method_side_effect, expected_result):
    tool = Tool(credentials_path='fake_credentials.json', sender_email='test@example.com')
    mock_service = MagicMock()
    mock_build.return_value = mock_service
    mock_send = mock_service.users.return_value.messages.return_value.send.return_value.execute
    mock_send.side_effect = send_method_side_effect

    mock_create_message.return_value = {'raw': 'fake_message'}

    result = tool('recipient@example.com', 'Test Subject', 'Test HTML Message')

    mock_authenticate.assert_called_once()
    mock_create_message.assert_called_once_with('recipient@example.com', 'Test Subject', 'Test HTML Message')
    mock_service.users().messages().send.assert_called_once_with(userId='me', body={'raw': 'fake_message'})
    assert result == expected_result
