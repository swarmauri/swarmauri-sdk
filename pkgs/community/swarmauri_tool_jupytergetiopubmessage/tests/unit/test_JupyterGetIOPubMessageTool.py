"""
Unit tests for the JupyterGetIOPubMessageTool class.

This module contains pytest-based test cases for verifying the functionality and correctness
of the JupyterGetIOPubMessageTool class. It uses mock WebSocket objects to simulate the
behavior of a Jupyter kernel connection.
"""

import sys
import time
import types
import json
import pytest
from unittest.mock import MagicMock, patch
from swarmauri_tool_jupytergetiopubmessage.JupyterGetIOPubMessageTool import (
    JupyterGetIOPubMessageTool,
)


@pytest.fixture
def mock_websocket(monkeypatch):
    """Create a mock WebSocket module with controllable messages."""
    messages = []

    class DummyTimeout(Exception):
        pass

    ws = MagicMock()

    def recv() -> str:
        if messages:
            return messages.pop(0)
        raise DummyTimeout()

    ws.recv.side_effect = recv
    ws.settimeout = MagicMock()
    ws._messages = messages

    def create_connection(url: str, timeout: float | None = None):
        return ws

    dummy_module = types.SimpleNamespace(
        create_connection=create_connection,
        WebSocketTimeoutException=DummyTimeout,
    )

    monkeypatch.setitem(sys.modules, "websocket", dummy_module)
    return ws


def test_init():
    """
    Tests the basic attributes of the JupyterGetIOPubMessageTool upon instantiation.
    """
    tool = JupyterGetIOPubMessageTool()
    assert tool.version == "1.0.0", "Tool version should be 1.0.0"
    assert tool.name == "JupyterGetIOPubMessageTool", "Tool name is incorrect"
    assert tool.description.startswith("Retrieves IOPub messages"), (
        "Tool description is incorrect"
    )
    assert tool.type == "JupyterGetIOPubMessageTool", (
        "Tool type should match class literal"
    )

    # Check parameters
    assert len(tool.parameters) == 2, (
        "Should have two parameters: channels_url and timeout"
    )

    param_names = {p.name for p in tool.parameters}
    assert "channels_url" in param_names, "Missing 'channels_url' parameter"
    assert "timeout" in param_names, "Missing 'timeout' parameter"


def test_retrieves_messages(mock_websocket):
    """
    Tests that JupyterGetIOPubMessageTool correctly retrieves various IOPub messages and stops
    on an idle status message without timing out.
    """
    # Prepare mock messages
    mock_websocket._messages.extend(
        [
            json.dumps(
                {
                    "msg_type": "stream",
                    "content": {"name": "stdout", "text": "Hello from stdout\n"},
                }
            ),
            json.dumps(
                {
                    "msg_type": "stream",
                    "content": {"name": "stderr", "text": "Warning: something\n"},
                }
            ),
            json.dumps(
                {
                    "msg_type": "execute_result",
                    "content": {"data": {"text/plain": "Execution result"}},
                }
            ),
            json.dumps({"msg_type": "status", "content": {"execution_state": "idle"}}),
        ]
    )

    tool = JupyterGetIOPubMessageTool()
    result = tool("ws://test/api/kernels/1/channels", timeout=2.0)

    assert result["timeout_exceeded"] is False, "Should not have exceeded timeout"
    assert len(result["stdout"]) == 1, "Should have captured one stdout message"
    assert "Hello from stdout" in result["stdout"][0]
    assert len(result["stderr"]) == 1, "Should have captured one stderr message"
    assert "Warning: something" in result["stderr"][0]
    assert len(result["execution_results"]) == 1, "Should have one execution result"
    assert "text/plain" in result["execution_results"][0], (
        "Execution result data missing"
    )
    assert result["logs"] == [], "Should not have any generic logs in this scenario"


@pytest.mark.parametrize("idle_messages", [[], None])
def test_timeout(mock_websocket, idle_messages):
    """
    Tests that JupyterGetIOPubMessageTool correctly reports a timeout when no idle status message
    is received within the specified duration.
    """
    # Add messages that never include an idle status.
    mock_websocket._messages.extend(
        [
            json.dumps(
                {
                    "msg_type": "stream",
                    "content": {"name": "stdout", "text": "Still running...\n"},
                }
            ),
            json.dumps(
                {
                    "msg_type": "stream",
                    "content": {"name": "stdout", "text": "More output...\n"},
                }
            ),
        ]
    )

    # Patch time.time to simulate passage of time so we trigger timeout quickly.
    with patch.object(time, "time") as mock_time:
        start = 1000.0
        # Create a list of timestamps. Once exhausted, fake_time() will always return the final time.
        times = [start, start + 1.0, start + 1.5, start + 2.0, start + 2.5]

        def fake_time():
            if times:
                return times.pop(0)
            return start + 2.5

        mock_time.side_effect = fake_time

        tool = JupyterGetIOPubMessageTool()
        result = tool("ws://test/api/kernels/1/channels", timeout=2.0)

    assert result["timeout_exceeded"] is True, "Should have exceeded timeout"
    assert len(result["stdout"]) == 2, (
        "Should capture all stdout messages before timeout"
    )


def test_error_handling(mock_websocket):
    """
    Tests that JupyterGetIOPubMessageTool handles error messages properly and logs the traceback.
    """
    error_traceback = [
        "Traceback (most recent call last):",
        '  File "<ipython-input-1>"',
        "NameError: name 'x' is not defined",
    ]
    mock_websocket._messages.extend(
        [
            json.dumps(
                {"msg_type": "error", "content": {"traceback": error_traceback}}
            ),
            json.dumps({"msg_type": "status", "content": {"execution_state": "idle"}}),
        ]
    )

    tool = JupyterGetIOPubMessageTool()
    result = tool("ws://test/api/kernels/1/channels", timeout=2.0)

    assert result["timeout_exceeded"] is False, (
        "Should not exceed timeout with valid idle message"
    )
    assert len(result["stderr"]) == 1, "Should capture one error message"
    assert "NameError: name 'x' is not defined" in result["stderr"][0], (
        "Error content not captured"
    )

    assert result["stdout"] == [], "No stdout messages expected"
    assert result["execution_results"] == [], "No execution results expected"
    assert result["logs"] == [], "No extra logs expected in this scenario"
