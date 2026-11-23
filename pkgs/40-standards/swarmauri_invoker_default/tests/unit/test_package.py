"""Verify the installed component's public contract and discovery."""

from importlib.metadata import distribution
import pytest
from swarmauri_invoker_default import DefaultInvoker, __version__
from swarmauri_base.invocations import InvokerBase


@pytest.mark.unit
def test_installed_component_contract():
    assert issubclass(DefaultInvoker, InvokerBase)
    installed = distribution("swarmauri_invoker_default")
    assert installed.version == __version__
    entry = next(
        e for e in installed.entry_points if e.name == "DefaultInvoker"
    )
    assert entry.group == "swarmauri.invocations"
    assert entry.load() is DefaultInvoker
