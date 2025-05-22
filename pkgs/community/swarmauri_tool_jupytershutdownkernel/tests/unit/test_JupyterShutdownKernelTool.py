import inspect
from unittest.mock import patch, MagicMock
from typing import Dict
import httpx

from swarmauri_tool_jupytershutdownkernel.JupyterShutdownKernelTool import (
    JupyterShutdownKernelTool,
)
from swarmauri_base.tools.ToolBase import ToolBase



class TestJupyterShutdownKernelTool:
    """
    Test suite for the JupyterShutdownKernelTool class.
    """

    def test_class_inheritance(self) -> None:
        tool = JupyterShutdownKernelTool()
        assert isinstance(tool, ToolBase), (
            "JupyterShutdownKernelTool does not inherit from ToolBase."
        )

    def test_initial_attributes(self) -> None:
        tool = JupyterShutdownKernelTool()
        assert tool.name == "JupyterShutdownKernelTool"
        assert (
            tool.description
            == "Shuts down a running Jupyter kernel and releases associated resources."
        )
        assert tool.type == "JupyterShutdownKernelTool"
        assert isinstance(tool.parameters, list), "Parameters should be a list."

        # Check parameters exist
        kernel_id_param = next(
            (p for p in tool.parameters if p.name == "kernel_id"), None
        )
        timeout_param = next(
            (p for p in tool.parameters if p.name == "shutdown_timeout"), None
        )

        assert kernel_id_param is not None, "Missing required parameter 'kernel_id'."
        assert kernel_id_param.required is True, (
            "Parameter 'kernel_id' should be required."
        )
        assert timeout_param is not None, (
            "Missing optional parameter 'shutdown_timeout'."
        )

        # Instead of checking the Parameter instance for a default value,
        # inspect the __call__ method signature to confirm the default value is 5.
        sig = inspect.signature(tool.__call__)
        assert sig.parameters["shutdown_timeout"].default == 5, (
            "Default shutdown timeout should be 5."
        )

    @patch(
        "swarmauri_tool_jupytershutdownkernel.JupyterShutdownKernelTool.jupyter_rest_client"
    )
    def test_call_success(self, mock_client: MagicMock) -> None:
        mock_response = MagicMock()
        mock_response.raise_for_status.return_value = None
        mock_response.json.return_value = {
            "status": "success",
            "message": "Kernel shut down successfully.",
        }
        mock_client.shutdown_kernel.return_value = mock_response

        tool = JupyterShutdownKernelTool()
        result: Dict[str, str] = tool(kernel_id="test_kernel")

        assert result["status"] == "success"
        assert "shut down successfully" in result["message"]
        mock_client.shutdown_kernel.assert_called_with("test_kernel")

    @patch(
        "swarmauri_tool_jupytershutdownkernel.JupyterShutdownKernelTool.jupyter_rest_client"
    )
    def test_call_http_error(self, mock_client: MagicMock) -> None:
        request = httpx.Request("DELETE", "http://localhost")
        response = httpx.Response(500, request=request, json={"message": "fail"})
        mock_client.shutdown_kernel.side_effect = httpx.HTTPStatusError(
            "Server error", request=request, response=response
        )

        tool = JupyterShutdownKernelTool()
        result = tool(kernel_id="test_kernel")

        assert result["status"] == "error"
        assert "fail" in result["message"]

    @patch(
        "swarmauri_tool_jupytershutdownkernel.JupyterShutdownKernelTool.jupyter_rest_client"
    )
    def test_call_unexpected_exception(self, mock_client: MagicMock) -> None:
        mock_client.shutdown_kernel.side_effect = RuntimeError("boom")

        tool = JupyterShutdownKernelTool()
        result = tool(kernel_id="faulty_kernel")

        assert result["status"] == "error"
        assert "unexpected error" in result["message"].lower()
