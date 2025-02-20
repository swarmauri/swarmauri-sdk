"""
test_JupyterGetShellMessageTool.py

This module contains pytest-based unit tests for the JupyterGetShellMessageTool class.
The tests ensure the tool correctly retrieves shell messages from a Jupyter kernel,
handles timeouts, and manages exceptions.
"""

import pytest
from unittest.mock import patch, MagicMock
from swarmauri_tool_jupytergetshellmessage.JupyterGetShellMessageTool import (
    JupyterGetShellMessageTool,
)


def test_class_attributes() -> None:
    """
    Test that the class attributes match the expected default values and types.
    """
    tool = JupyterGetShellMessageTool()
    assert tool.version == "1.0.0", "Version attribute should be '1.0.0'."
    assert tool.name == "JupyterGetShellMessageTool", "Unexpected name attribute."
    assert tool.type == "JupyterGetShellMessageTool", "Unexpected tool type."
    assert "timeout" in [
        param.name for param in tool.parameters
    ], "Parameter 'timeout' should be in the parameters list."


@pytest.mark.parametrize("timeout_value", [0.1, 1.0, 5.0])
def test_call_method_no_messages(timeout_value: float) -> None:
    """
    Verify that calling the tool with no messages available returns
    an error indicating no shell messages were received.
    """
    mock_client = MagicMock()
    # Simulate no messages on the shell channel
    mock_client.shell_channel.msg_ready.return_value = False

    with patch(
        "swarmauri_tool_jupytergetshellmessage.JupyterGetShellMessageTool.find_connection_file",
        return_value="fake_connection_file",
    ), patch(
        "swarmauri_tool_jupytergetshellmessage.JupyterGetShellMessageTool.BlockingKernelClient",
        return_value=mock_client,
    ):
        tool = JupyterGetShellMessageTool()
        result = tool(timeout=timeout_value)
        assert "error" in result, "Expected an error when no messages are available."


def test_call_method_with_messages() -> None:
    """
    Verify that the tool retrieves shell messages correctly.
    """
    from itertools import chain, repeat

    with patch(
        "swarmauri_tool_jupytergetshellmessage.JupyterGetShellMessageTool.find_connection_file",
        return_value="/path/to/fake/connection_file.json",
    ), patch(
        "swarmauri_tool_jupytergetshellmessage.JupyterGetShellMessageTool.BlockingKernelClient"
    ) as MockClient:
        mock_client_instance = MockClient.return_value
        # Use an iterator that returns True once and then False indefinitely
        mock_client_instance.shell_channel.msg_ready.side_effect = chain(
            [True], repeat(False)
        )
        mock_client_instance.shell_channel.get_msg.return_value = {
            "content": {"text": "Hello, world!"}
        }

        tool = JupyterGetShellMessageTool()
        result = tool(timeout=1.0)
        assert "messages" in result, "Expected 'messages' key in result."
        assert len(result["messages"]) == 1, "Expected exactly one retrieved message."
        assert (
            result["messages"][0]["content"]["text"] == "Hello, world!"
        ), "Message content does not match expected value."


def test_call_method_exception_handling() -> None:
    """
    Verify that when an exception occurs during message retrieval,
    the tool returns an error dictionary.
    """
    # Here we force find_connection_file to raise an exception.
    with patch(
        "swarmauri_tool_jupytergetshellmessage.JupyterGetShellMessageTool.find_connection_file",
        side_effect=RuntimeError("Test Error"),
    ), patch(
        "swarmauri_tool_jupytergetshellmessage.JupyterGetShellMessageTool.BlockingKernelClient",
        side_effect=RuntimeError("Test Error"),
    ):
        tool = JupyterGetShellMessageTool()
        result = tool()
        assert "error" in result, "Expected an error when exception is raised."
        assert (
            "Test Error" in result["error"]
        ), "Expected 'Test Error' in the error message."
