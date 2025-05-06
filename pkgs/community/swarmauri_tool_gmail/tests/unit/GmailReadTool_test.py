import pytest
from swarmauri_tool_gmail.GmailReadTool import (
    GmailReadTool as Tool,
)
from unittest.mock import patch, MagicMock


@pytest.fixture
def tool():
    return Tool(
        credentials_path="fake_credentials.json",
        sender_email="test@example.com",
    )


@pytest.fixture
def mock_gmail_service():
    mock_service = MagicMock()
    mock_messages = MagicMock()
    mock_service.users().messages.return_value = mock_messages
    mock_list = MagicMock()
    mock_messages.list.return_value = mock_list
    mock_list.execute.return_value = {"messages": [{"id": "msg1"}, {"id": "msg2"}]}
    mock_get = MagicMock()
    mock_messages.get.return_value = mock_get
    mock_get.execute.return_value = {
        "payload": {
            "headers": [
                {"name": "From", "value": "sender@example.com"},
                {"name": "Subject", "value": "Test Subject"},
                {"name": "Date", "value": "2023-01-01 12:00:00"},
            ]
        }
    }
    return mock_service


@pytest.mark.unit
def test_type(tool):
    assert tool.type == "GmailReadTool"


@pytest.mark.unit
def test_resource(tool):
    assert tool.resource == "Tool"


@pytest.mark.unit
def test_serialization(tool):
    tool_dict = tool.model_dump()
    assert tool_dict["name"] == "GmailReadTool"
    assert tool_dict["description"] == "Read emails from a Gmail account."
    assert len(tool_dict["parameters"]) == 2
    assert all(
        param["name"] in ["query", "max_results"] for param in tool_dict["parameters"]
    )


@pytest.mark.unit
@patch("google.oauth2.service_account.Credentials.from_service_account_file")
@patch("googleapiclient.discovery.build")
def test_authenticate(mock_build, mock_credentials, tool):
    mock_credentials_instance = MagicMock()
    mock_credentials.return_value = mock_credentials_instance
    mock_credentials_instance.with_subject.return_value = mock_credentials_instance
    mock_service = MagicMock()
    mock_build.return_value = mock_service

    assert tool.service is None

    tool.authenticate()

    mock_credentials.assert_called_once_with(tool.credentials_path, scopes=tool.SCOPES)
    mock_credentials_instance.with_subject.assert_called_once_with(tool.sender_email)

    assert tool.service is not None


@pytest.mark.unit
@patch.object(Tool, "authenticate")
def test_call(mock_authenticate, tool, mock_gmail_service):
    tool.service = mock_gmail_service

    result = tool(query="is:unread", max_results=2)

    mock_authenticate.assert_called_once()
    mock_gmail_service.users().messages().list.assert_called_once_with(
        userId="me", q="is:unread", maxResults=2
    )
    assert "gmail_messages" in result
    assert "sender@example.com" in result["gmail_messages"]
    assert "Test Subject" in result["gmail_messages"]


@pytest.mark.unit
def test_invalid_credentials(tool):
    with patch.object(
        Tool, "authenticate", side_effect=Exception("Invalid credentials")
    ):
        result = tool(query="is:unread")
        assert "An error occurred" in result, f"{result}"
        assert "Invalid credentials" in result
