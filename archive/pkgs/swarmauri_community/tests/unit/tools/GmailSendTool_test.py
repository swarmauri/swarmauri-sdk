from unittest.mock import patch, MagicMock

import pytest
from swarmauri_community.tools.concrete.GmailSendTool import (
    GmailSendTool as Tool,
)


@pytest.mark.unit
def test_ubc_resource():
    tool = Tool(
        credentials_path="fake_credentials.json",
        sender_email="test@example.com",
        service={"serviceName": "gmail", "version": "v1"},
    )
    assert tool.resource == "Tool"


@pytest.mark.unit
def test_ubc_type():
    assert (
        Tool(
            credentials_path="fake_credentials.json",
            sender_email="test@example.com",
            service={"serviceName": "gmail", "version": "v1"},
        ).type
        == "GmailSendTool"
    )


@pytest.mark.unit
def test_initialization():
    tool = Tool(
        credentials_path="fake_credentials.json",
        sender_email="test@example.com",
        service={"serviceName": "gmail", "version": "v1"},
    )
    assert type(tool.id) is str


@pytest.mark.unit
def test_serialization():
    tool = Tool(
        credentials_path="fake_credentials.json",
        sender_email="test@example.com",
        service={"serviceName": "gmail", "version": "v1"},
    )
    assert tool.id == Tool.model_validate_json(tool.model_dump_json()).id


@patch.object(Tool, "authenticate")
@patch.object(Tool, "create_message")
@patch("googleapiclient.discovery.build")
def test_send_email_success(mock_build, mock_create_message, mock_authenticate):
    # Initialize the tool with mock credentials and sender email
    tool = Tool(
        credentials_path="fake_credentials.json",
        sender_email="test@example.com",
        service={"serviceName": "gmail", "version": "v1"},
    )

    # Mock the Gmail service and the entire chain of methods
    mock_service = MagicMock()
    mock_build.return_value = mock_service
    mock_users = mock_service.users.return_value
    mock_messages = mock_users.messages.return_value
    mock_send = mock_messages.send.return_value
    mock_send.execute.return_value = None  # Simulate successful send

    # Mock the create_message method to return a dummy message
    mock_create_message.return_value = {"raw": "dummy_message"}

    # Call the method to send an email
    result = tool(
        "recipient@example.com", "Test Subject", "<p>This is a test email.</p>"
    )

    # Assert that the result is a dictionary
    assert isinstance(result, dict)

    # Assert that the email was sent successfully
    assert result == {"success": "Email sent successfully to recipient@example.com"}

    # Check that authenticate and create_message were called with correct arguments
    mock_authenticate.assert_called_once()
    mock_create_message.assert_called_once_with(
        "recipient@example.com", "Test Subject", "<p>This is a test email.</p>"
    )
