"""Unit tests for the JupyterShutdownKernelTool component.

This module uses pytest to verify the functionality and correctness of the
JupyterShutdownKernelTool class. It checks that the tool can be instantiated, that
it inherits from the correct base classes, and that its shutdown logic behaves
as expected in different scenarios.
"""

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

    Ensures that the tool is correctly initialized, inherits from the appropriate
    base class, contains the right parameters, and properly handles various
    shutdown scenarios.
    """

    def test_class_inheritance(self) -> None:
        """
        Test that JupyterShutdownKernelTool inherits from ToolBase.
        """
        tool = JupyterShutdownKernelTool()
        assert isinstance(tool, ToolBase), "JupyterShutdownKernelTool does not inherit from ToolBase."

    def test_initial_attributes(self) -> None:
        """
        Test the tool's default attribute values.
        """
        tool = JupyterShutdownKernelTool()
        assert tool.version == "1.0.0"
        assert tool.name == "JupyterShutdownKernelTool"
        assert tool.description == "Shuts down a running Jupyter kernel and releases associated resources."
        assert tool.type == "JupyterShutdownKernelTool"
        assert isinstance(tool.parameters, list), "Parameters should be a list."

        # Check parameters
        kernel_id_param = next((p for p in tool.parameters if p.name == "kernel_id"), None)
        timeout_param = next((p for p in tool.parameters if p.name == "shutdown_timeout"), None)

        assert kernel_id_param is not None, "Missing required parameter 'kernel_id'."
        assert kernel_id_param.required is True, "Parameter 'kernel_id' should be required."
        assert timeout_param is not None, "Missing optional parameter 'shutdown_timeout'."
        assert timeout_param.default == 5, "Default shutdown timeout should be 5."

    @patch("swarmauri_tool_jupytershutdownkernel.JupyterShutdownKernelTool.KernelManager")
    def test_call_success(self, mock_kernel_manager: MagicMock) -> None:
        """
        Test a successful kernel shutdown scenario.
        """
        mock_manager_instance = mock_kernel_manager.return_value
        # Simulate kernel shutting down before timeout
        mock_manager_instance.is_alive.side_effect = [True, False]

        tool = JupyterShutdownKernelTool()
        result: Dict[str, str] = tool(kernel_id="test_kernel")

        assert result["status"] == "success"
        assert "shut down successfully" in result["message"]
        mock_manager_instance.shutdown_kernel.assert_called_with(now=False)

    @patch("swarmauri_tool_jupytershutdownkernel.JupyterShutdownKernelTool.KernelManager")
    def test_call_forced_shutdown(self, mock_kernel_manager: MagicMock) -> None:
        """
        Test the scenario where a kernel does not shut down gracefully and requires a forced shutdown.
        """
        mock_manager_instance = mock_kernel_manager.return_value
        # Simulate kernel still alive after waiting
        mock_manager_instance.is_alive.side_effect = [True, True, True]

        tool = JupyterShutdownKernelTool()
        result: Dict[str, str] = tool(kernel_id="test_kernel", shutdown_timeout=1)

        assert result["status"] == "error"
        assert "could not be shut down" in result["message"]
        # Ensure forced shutdown is attempted
        mock_manager_instance.shutdown_kernel.assert_any_call(now=True)

    @patch("swarmauri_tool_jupytershutdownkernel.JupyterShutdownKernelTool.KernelManager")
    def test_call_no_such_kernel(self, mock_kernel_manager: MagicMock) -> None:
        """
        Test the scenario where the specified kernel does not exist.
        """
        mock_manager_instance = mock_kernel_manager.return_value
        # Raise NoSuchKernel when load_connection_file is called
        mock_manager_instance.load_connection_file.side_effect = NoSuchKernel

        tool = JupyterShutdownKernelTool()
        result: Dict[str, str] = tool(kernel_id="non_existent")

        assert result["status"] == "error"
        assert "No such kernel" in result["message"]

    @patch("swarmauri_tool_jupytershutdownkernel.JupyterShutdownKernelTool.KernelManager")
    def test_call_connection_file_not_found(self, mock_kernel_manager: MagicMock) -> None:
        """
        Test the scenario where a connection file is not found for the specified kernel.
        """
        mock_manager_instance = mock_kernel_manager.return_value
        mock_manager_instance.load_connection_file.side_effect = FileNotFoundError

        tool = JupyterShutdownKernelTool()
        result: Dict[str, str] = tool(kernel_id="missing_connection_file")

        assert result["status"] == "error"
        assert "Connection file not found" in result["message"]

    @patch("swarmauri_tool_jupytershutdownkernel.JupyterShutdownKernelTool.KernelManager")
    def test_call_unexpected_exception(self, mock_kernel_manager: MagicMock) -> None:
        """
        Test the scenario where an unexpected exception is raised during kernel shutdown.
        """
        mock_manager_instance = mock_kernel_manager.return_value
        mock_manager_instance.load_connection_file.side_effect = RuntimeError("Unexpected error")

        tool = JupyterShutdownKernelTool()
        result: Dict[str, str] = tool(kernel_id="faulty_kernel")

        assert result["status"] == "error"
        assert "unexpected error" in result["message"].lower()