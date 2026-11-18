"""Verify the installed component's public contract and discovery."""

from importlib.metadata import distribution
import pytest
from swarmauri_taskstore_sqlite import SqliteTaskStore, __version__
from swarmauri_base.tasks import TaskStoreBase


@pytest.mark.unit
def test_installed_component_contract():
    assert issubclass(SqliteTaskStore, TaskStoreBase)
    installed = distribution("swarmauri_taskstore_sqlite")
    assert installed.version == __version__
    entry = next(
        e for e in installed.entry_points if e.name == "SqliteTaskStore"
    )
    assert entry.group == "swarmauri.task_stores"
    assert entry.load() is SqliteTaskStore
