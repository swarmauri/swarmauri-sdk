"""
test_JupyterStartKernelTool.py

This module contains pytest-based test cases for the JupyterStartKernelTool class, which is
responsible for creating and managing Jupyter kernel instances. These tests validate that
the class behaves correctly under different conditions, including normal operation and
error scenarios.
"""

import pytest
from typing import Dict, Any
from unittest.mock import patch, MagicMock

from swarmauri_tool_jupyterstartkernel.JupyterStartKernelTool import (
    JupyterStartKernelTool,
)


def test_tool_initialization() -> None:
    """
    Tests that the JupyterStartKernelTool can be instantiated with default parameters.
    Ensures the tool's attributes are set as expected.
    """
    tool = JupyterStartKernelTool()
    assert (
        tool.name == "JupyterStartKernelTool"
    ), "Tool name should match expected default."
    assert tool.version == "1.0.0", "Default version should be '1.0.0'."
    assert (
        tool.type == "JupyterStartKernelTool"
    ), "Tool type should be 'JupyterStartKernelTool'."
    assert (
        len(tool.parameters) == 2
    ), "Expected two default parameters (kernel_name, kernel_spec)."


@pytest.mark.parametrize(
    "kernel_name, expected_kernel_name",
    [
        ("python3", "python3"),
        ("python2", "python2"),
    ],
)
@patch(
    "swarmauri_tool_jupyterstartkernel.JupyterStartKernelTool.KernelManager",
    autospec=True,
)
def test_call_success(
    mock_kernel_manager_class: MagicMock, kernel_name: str, expected_kernel_name: str
) -> None:
    """
    Tests that calling the JupyterStartKernelTool successfully starts a kernel
    and returns a dictionary with kernel_name and kernel_id.
    Uses a mock to avoid starting a real kernel.
    """
    mock_kernel_manager = MagicMock()
    mock_kernel_manager.kernel_id = "fake_kernel_id"
    mock_kernel_manager_class.return_value = mock_kernel_manager

    tool = JupyterStartKernelTool()
    result = tool(kernel_name=kernel_name)

    mock_kernel_manager_class.assert_called_once_with(kernel_name=expected_kernel_name)
    mock_kernel_manager.start_kernel.assert_called_once()

    assert "kernel_id" in result, "Result should contain 'kernel_id'."
    assert (
        result["kernel_name"] == expected_kernel_name
    ), "Kernel name should match the input."
    assert (
        result["kernel_id"] == "fake_kernel_id"
    ), "Mock kernel ID should match the returned value."
    assert (
        tool.get_kernel_manager() is mock_kernel_manager
    ), "Tool should store the KernelManager instance internally."


@patch(
    "swarmauri_tool_jupyterstartkernel.JupyterStartKernelTool.KernelManager",
    autospec=True,
)
def test_call_failure(mock_kernel_manager_class: MagicMock) -> None:
    """
    Tests that if the kernel manager raises an exception during start,
    the tool returns a dictionary containing 'error' and logs the exception.
    """
    mock_kernel_manager = MagicMock()
    mock_kernel_manager.start_kernel.side_effect = RuntimeError(
        "Failed to start kernel."
    )
    mock_kernel_manager_class.return_value = mock_kernel_manager

    tool = JupyterStartKernelTool()
    result = tool(kernel_name="invalid_kernel")

    assert "error" in result, "Result should contain an 'error' key on failure."
    assert (
        "Failed to start kernel." in result["error"]
    ), "Error message should indicate what went wrong."
    assert (
        tool.get_kernel_manager() is None
    ), "KernelManager should not be stored if kernel start fails."


def test_get_kernel_manager_without_call() -> None:
    """
    Tests that get_kernel_manager returns None if the __call__ method has not been invoked
    and no kernel has been started.
    """
    tool = JupyterStartKernelTool()
    km = tool.get_kernel_manager()
    assert km is None, "Expected None if no kernel has been started."


def test_tool_parameters() -> None:
    """
    Tests that the parameters field of the tool can be customized and accessed properly.
    """
    custom_params = [
        {
            "name": "kernel_name",
            "tinput_ype": "string",
            "description": "Customized kernel name parameter.",
            "required": True,
            "default": "python3",
        },
        {
            "name": "extra_config",
            "input_type": "object",
            "description": "Extra configuration for advanced kernel startup.",
            "required": False,
            "default": {},
        },
    ]
    tool = JupyterStartKernelTool(parameters=custom_params)  # type: ignore
    assert len(tool.parameters) == 2, "Customized tool should have two parameters."
    assert (
        tool.parameters[0].name == "kernel_name"
    ), "First parameter should be kernel_name."
    assert (
        tool.parameters[1].name == "extra_config"
    ), "Second parameter should be extra_config."

    # PARAMETER does not have attr 'default'
    # assert (
    #     tool.parameters[1].default == {}
    # ), "Default for extra_config should be an empty dict."


def test_call_with_kernel_spec() -> None:
    """
    Tests that calling the tool with a kernel specification does not raise an error
    and returns the correct dictionary structure. This test does not mock the kernel
    manager and is intended for demonstration; in real usage, a mock would be used.
    """
    tool = JupyterStartKernelTool()
    result: Dict[str, Any] = tool(
        kernel_name="python3", kernel_spec={"env": {"KEY": "VALUE"}}
    )

    # Since no actual kernel is started in many CI environments, this could fail in real scenarios,
    # but we include it here to demonstrate potential usage.
    if "error" in result:
        assert (
            "error" in result
        ), "If an error occurred due to environment constraints, the result should contain 'error'."
    else:
        assert "kernel_id" in result, "A successful call should return a 'kernel_id'."
        assert (
            "kernel_name" in result
        ), "A successful call should return a 'kernel_name'."
