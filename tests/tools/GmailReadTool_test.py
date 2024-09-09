import pytest
from swarmauri.community.tools.concrete.GmailReadTool import GmailReadTool as Tool
from unittest.mock import patch, MagicMock
import json

@pytest.fixture
def tool():
    return Tool(credentials_path='path/to/credentials.json', sender_email='test@example.com')

@pytest.mark.unit
def test_type(tool):
    assert tool.type == 'GmailReadTool'

@pytest.mark.unit
def test_resource(tool):
    assert tool.resource == 'Tool'

@pytest.mark.unit
def test_serialization(tool):
    tool_dict = tool.dict()
    assert tool_dict['name'] == 'GmailReadTool'
    assert tool_dict['description'] == 'Read emails from a Gmail account.'
    assert len(tool_dict['parameters']) == 2
    assert all(param['name'] in ['query', 'max_results'] for param in tool_dict['parameters'])

@pytest.mark.unit
@patch.object(Tool, 'authenticate', return_value=None)
@patch('googleapiclient.discovery.build')
def test_access(mock_build, mock_authenticate, tool):
    mock_service = MagicMock()
    mock_build.return_value = mock_service
    mock_service.users.return_value.messages.return_value.list.return_value.execute.return_value = {'messages': []}

    result = tool(query='is:unread', max_results=10)
    mock_build.assert_called_once_with('gmail', 'v1', credentials=MagicMock())
    assert isinstance(result, str)
    assert 'sender:' in result

@pytest.mark.unit
@patch.object(Tool, 'authenticate', return_value=None)
@patch('googleapiclient.discovery.build')
def test_call(mock_build, mock_authenticate, tool):
    mock_service = MagicMock()
    mock_build.return_value = mock_service
    mock_service.users.return_value.messages.return_value.list.return_value.execute.return_value = {
        'messages': [{'threadId': '123'}]
    }
    mock_service.users.return_value.messages.return_value.get.return_value.execute.return_value = {
        'payload': {
            'headers': [
                {'name': 'From', 'value': 'test@example.com'},
                {'name': 'Subject', 'value': 'Test Subject'},
                {'name': 'Reply-To', 'value': 'reply@example.com'},
                {'name': 'Date', 'value': '2024-09-01'}
            ]
        }
    }

    result = tool(query='is:unread', max_results=10)
    assert 'sender:test@example.com' in result
    assert 'reply-to:reply@example.com' in result
    assert 'subject: Test Subject' in result
    assert 'date_time:2024-09-01' in result
