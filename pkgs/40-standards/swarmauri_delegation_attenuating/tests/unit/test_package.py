"""Verify the installed component's public contract and discovery."""

from importlib.metadata import distribution
import pytest
from swarmauri_delegation_attenuating import (
    AttenuatingDelegationService,
    __version__,
)
from swarmauri_base.delegation import DelegationServiceBase


@pytest.mark.unit
def test_installed_component_contract():
    assert issubclass(AttenuatingDelegationService, DelegationServiceBase)
    installed = distribution("swarmauri_delegation_attenuating")
    assert installed.version == __version__
    entry = next(
        e
        for e in installed.entry_points
        if e.name == "AttenuatingDelegationService"
    )
    assert entry.group == "swarmauri.delegations"
    assert entry.load() is AttenuatingDelegationService
