import inspect
import pytest
from unittest.mock import patch, MagicMock
from typing import Dict

from swarmauri_tool_jupytershutdownkernel.JupyterShutdownKernelTool import JupyterShutdownKernelTool
from swarmauri_standard.tools.Parameter import Parameter
from swarmauri_base.tools.ToolBase import ToolBase
from jupyter_client.kernelspec import NoSuchKernel


class TestJupyterShutdownKernelTool:
    """
    Test suite for the JupyterShutdownKernelTool class.
    """

    def test_class_inheritance(self) -> None:
        tool = JupyterShutdownKernelTool()
        assert isinstance(tool, ToolBase), "JupyterShutdownKernelTool does not inherit from ToolBase."

    def test_initial_attributes(self) -> None:
        tool = JupyterShutdownKernelTool()
        assert tool.name == "JupyterShutdownKernelTool"
        assert tool.description == "Shuts down a running Jupyter kernel and releases associated resources."
        assert tool.type == "JupyterShutdownKernelTool"
        assert isinstance(tool.parameters, list), "Parameters should be a list."

        # Check parameters exist
        kernel_id_param = next((p for p in tool.parameters if p.name == "kernel_id"), None)
        timeout_param = next((p for p in tool.parameters if p.name == "shutdown_timeout"), None)

        assert kernel_id_param is not None, "Missing required parameter 'kernel_id'."
        assert kernel_id_param.required is True, "Parameter 'kernel_id' should be required."
        assert timeout_param is not None, "Missing optional parameter 'shutdown_timeout'."

        # Instead of checking the Parameter instance for a default value,
        # inspect the __call__ method signature to confirm the default value is 5.
        sig = inspect.signature(tool.__call__)
        assert sig.parameters["shutdown_timeout"].default == 5, "Default shutdown timeout should be 5."

    @patch("swarmauri_tool_jupytershutdownkernel.JupyterShutdownKernelTool.KernelManager")
    def test_call_success(self, mock_kernel_manager: MagicMock) -> None:
        mock_manager_instance = mock_kernel_manager.return_value
        # The shutdown logic calls is_alive() several times:
        # 1. While-loop condition (iteration 1)
        # 2. While-loop condition (iteration 2) → exit loop
        # 3. Forced shutdown check (should not be called)
        # 4. Final check confirming kernel is down
        mock_manager_instance.is_alive.side_effect = [True, False, False, False]

        tool = JupyterShutdownKernelTool()
        result: Dict[str, str] = tool(kernel_id="test_kernel")

        assert result["status"] == "success"
        assert "shut down successfully" in result["message"]
        mock_manager_instance.shutdown_kernel.assert_called_with(now=False)

    @patch("swarmauri_tool_jupytershutdownkernel.JupyterShutdownKernelTool.KernelManager")
    def test_call_forced_shutdown(self, mock_kernel_manager: MagicMock) -> None:
        mock_manager_instance = mock_kernel_manager.return_value
        # For forced shutdown, is_alive() is called multiple times:
        # Provide enough responses to cover all calls.
        mock_manager_instance.is_alive.side_effect = [True, True, True, True, True]

        tool = JupyterShutdownKernelTool()
        result: Dict[str, str] = tool(kernel_id="test_kernel", shutdown_timeout=1)

        assert result["status"] == "error"
        assert "could not be shut down" in result["message"]
        mock_manager_instance.shutdown_kernel.assert_any_call(now=True)

    @patch("swarmauri_tool_jupytershutdownkernel.JupyterShutdownKernelTool.KernelManager")
    def test_call_no_such_kernel(self, mock_kernel_manager: MagicMock) -> None:
        mock_manager_instance = mock_kernel_manager.return_value
        # Instantiate NoSuchKernel with a dummy argument.
        mock_manager_instance.load_connection_file.side_effect = NoSuchKernel("dummy")

        tool = JupyterShutdownKernelTool()
        result: Dict[str, str] = tool(kernel_id="non_existent")

        assert result["status"] == "error"
        assert "No such kernel" in result["message"]

    @patch("swarmauri_tool_jupytershutdownkernel.JupyterShutdownKernelTool.KernelManager")
    def test_call_connection_file_not_found(self, mock_kernel_manager: MagicMock) -> None:
        mock_manager_instance = mock_kernel_manager.return_value
        mock_manager_instance.load_connection_file.side_effect = FileNotFoundError

        tool = JupyterShutdownKernelTool()
        result: Dict[str, str] = tool(kernel_id="missing_connection_file")

        assert result["status"] == "error"
        assert "Connection file not found" in result["message"]

    @patch("swarmauri_tool_jupytershutdownkernel.JupyterShutdownKernelTool.KernelManager")
    def test_call_unexpected_exception(self, mock_kernel_manager: MagicMock) -> None:
        mock_manager_instance = mock_kernel_manager.return_value
        mock_manager_instance.load_connection_file.side_effect = RuntimeError("Unexpected error")

        tool = JupyterShutdownKernelTool()
        result: Dict[str, str] = tool(kernel_id="faulty_kernel")

        assert result["status"] == "error"
        assert "unexpected error" in result["message"].lower()
