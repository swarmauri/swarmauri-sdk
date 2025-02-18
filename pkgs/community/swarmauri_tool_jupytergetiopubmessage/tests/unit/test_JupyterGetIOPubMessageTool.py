"""
Unit tests for the JupyterGetIOPubMessageTool class.

This module contains pytest-based test cases for verifying the functionality and correctness
of the JupyterGetIOPubMessageTool class. It uses mock objects to simulate the behavior of a
Jupyter kernel client.
"""

import time
import pytest
from unittest.mock import MagicMock, patch
from swarmauri_tool_jupytergetiopubmessage.JupyterGetIOPubMessageTool import JupyterGetIOPubMessageTool


@pytest.fixture
def mock_kernel_client():
    """
    Pytest fixture that creates a mock Jupyter kernel client with a controllable sequence of messages.
    """
    client = MagicMock()
    messages = []

    def get_iopub_msg(timeout: float = 0.1):
        """
        Returns the next message from the predefined messages list if available, otherwise None.
        """
        if messages:
            return messages.pop(0)
        return None

    client.get_iopub_msg.side_effect = get_iopub_msg
    client._messages = messages  # Expose the list so tests can manipulate it as needed
    return client


def test_init():
    """
    Tests the basic attributes of the JupyterGetIOPubMessageTool upon instantiation.
    """
    tool = JupyterGetIOPubMessageTool()
    assert tool.version == "1.0.0", "Tool version should be 1.0.0"
    assert tool.name == "JupyterGetIOPubMessageTool", "Tool name is incorrect"
    assert tool.description.startswith("Retrieves IOPub messages"), "Tool description is incorrect"
    assert tool.type == "JupyterGetIOPubMessageTool", "Tool type should match class literal"

    # Check parameters
    assert len(tool.parameters) == 2, "Should have two parameters: kernel_client and timeout"
    param_names = {p.name for p in tool.parameters}
    assert "kernel_client" in param_names, "Missing 'kernel_client' parameter"
    assert "timeout" in param_names, "Missing 'timeout' parameter"


def test_retrieves_messages(mock_kernel_client):
    """
    Tests that JupyterGetIOPubMessageTool correctly retrieves various IOPub messages and stops
    on an idle status message without timing out.
    """
    # Prepare mock messages
    mock_kernel_client._messages.extend([
        {"msg_type": "stream", "content": {"name": "stdout", "text": "Hello from stdout\n"}},
        {"msg_type": "stream", "content": {"name": "stderr", "text": "Warning: something\n"}},
        {"msg_type": "execute_result", "content": {"data": {"text/plain": "Execution result"}}},
        {"msg_type": "status", "content": {"execution_state": "idle"}},
    ])

    tool = JupyterGetIOPubMessageTool()
    result = tool(kernel_client=mock_kernel_client, timeout=2.0)

    assert result["timeout_exceeded"] is False, "Should not have exceeded timeout"
    assert len(result["stdout"]) == 1, "Should have captured one stdout message"
    assert "Hello from stdout" in result["stdout"][0]
    assert len(result["stderr"]) == 1, "Should have captured one stderr message"
    assert "Warning: something" in result["stderr"][0]
    assert len(result["execution_results"]) == 1, "Should have one execution result"
    assert "text/plain" in result["execution_results"][0], "Execution result data missing"
    assert result["logs"] == [], "Should not have any generic logs in this scenario"


@pytest.mark.parametrize("idle_messages", [[], None])
def test_timeout(mock_kernel_client, idle_messages):
    """
    Tests that JupyterGetIOPubMessageTool correctly reports a timeout when no idle status message
    is received within the specified duration.
    """
    # Add messages that never include an idle status
    mock_kernel_client._messages.extend([
        {"msg_type": "stream", "content": {"name": "stdout", "text": "Still running...\n"}},
        {"msg_type": "stream", "content": {"name": "stdout", "text": "More output...\n"}},
    ])

    # Patch time.time to simulate passage of time so we trigger timeout quickly
    with patch.object(time, "time") as mock_time:
        start = 1000.0
        mock_time.side_effect = [start, start + 1.0, start + 2.1, start + 3.0, start + 4.0]

        tool = JupyterGetIOPubMessageTool()
        result = tool(kernel_client=mock_kernel_client, timeout=2.0)

    assert result["timeout_exceeded"] is True, "Should have exceeded timeout"
    assert len(result["stdout"]) == 2, "Should capture all stdout messages before timeout"
    assert result["stderr"] == [], "Should have no stderr messages"
    assert result["execution_results"] == [], "No execution results expected before timeout"


def test_error_handling(mock_kernel_client):
    """
    Tests that JupyterGetIOPubMessageTool handles error messages properly and logs the traceback.
    """
    error_traceback = [
        "Traceback (most recent call last):",
        "  File \"<ipython-input-1>\"",
        "NameError: name 'x' is not defined",
    ]
    mock_kernel_client._messages.extend([
        {"msg_type": "error", "content": {"traceback": error_traceback}},
        {"msg_type": "status", "content": {"execution_state": "idle"}},
    ])

    tool = JupyterGetIOPubMessageTool()
    result = tool(kernel_client=mock_kernel_client, timeout=2.0)

    assert result["timeout_exceeded"] is False, "Should not exceed timeout with valid idle message"
    assert len(result["stderr"]) == 1, "Should capture one error message"
    assert "NameError: name 'x' is not defined" in result["stderr"][0], "Error content not captured"
    assert result["stdout"] == [], "No stdout messages expected"
    assert result["execution_results"] == [], "No execution results expected"
    assert result["logs"] == [], "No extra logs expected in this scenario"