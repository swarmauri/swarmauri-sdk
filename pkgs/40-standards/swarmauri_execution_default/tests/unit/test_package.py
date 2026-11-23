"""Verify the installed component's public contract and discovery."""

from importlib.metadata import distribution
import pytest
from swarmauri_execution_default import DefaultExecutionController, __version__
from swarmauri_base.executions import ExecutionControllerBase


@pytest.mark.unit
def test_installed_component_contract():
    assert issubclass(DefaultExecutionController, ExecutionControllerBase)
    installed = distribution("swarmauri_execution_default")
    assert installed.version == __version__
    entry = next(
        e
        for e in installed.entry_points
        if e.name == "DefaultExecutionController"
    )
    assert entry.group == "swarmauri.executions"
    assert entry.load() is DefaultExecutionController
