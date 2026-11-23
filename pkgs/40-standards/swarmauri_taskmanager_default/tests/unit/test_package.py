"""Verify the installed component's public contract and discovery."""

from importlib.metadata import distribution
import pytest
from swarmauri_taskmanager_default import DefaultTaskManager, __version__
from swarmauri_base.tasks import TaskManagerBase


@pytest.mark.unit
def test_installed_component_contract():
    assert issubclass(DefaultTaskManager, TaskManagerBase)
    installed = distribution("swarmauri_taskmanager_default")
    assert installed.version == __version__
    entry = next(
        e for e in installed.entry_points if e.name == "DefaultTaskManager"
    )
    assert entry.group == "swarmauri.tasks"
    assert entry.load() is DefaultTaskManager
