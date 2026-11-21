"""Verify the installed component's public contract and discovery."""

from importlib.metadata import distribution
import pytest
from swarmauri_grantstore_sqlite import SqliteGrantStore, __version__
from swarmauri_base.delegation import GrantStoreBase


@pytest.mark.unit
def test_installed_component_contract():
    assert issubclass(SqliteGrantStore, GrantStoreBase)
    installed = distribution("swarmauri_grantstore_sqlite")
    assert installed.version == __version__
    entry = next(
        e for e in installed.entry_points if e.name == "SqliteGrantStore"
    )
    assert entry.group == "swarmauri.grant_stores"
    assert entry.load() is SqliteGrantStore
