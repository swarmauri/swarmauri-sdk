"""Verify the installed component's public contract and discovery."""

from importlib.metadata import distribution
import pytest
from swarmauri_permission_explicit import ExplicitPermissionPolicy, __version__
from swarmauri_base.permissions import PermissionPolicyBase


@pytest.mark.unit
def test_installed_component_contract():
    assert issubclass(ExplicitPermissionPolicy, PermissionPolicyBase)
    installed = distribution("swarmauri_permission_explicit")
    assert installed.version == __version__
    entry = next(
        e
        for e in installed.entry_points
        if e.name == "ExplicitPermissionPolicy"
    )
    assert entry.group == "swarmauri.permissions"
    assert entry.load() is ExplicitPermissionPolicy
