import pytest

from swarmauri.interface_registry import InterfaceRegistry


@pytest.fixture(autouse=True)
def restore_registry():
    original = InterfaceRegistry.INTERFACE_REGISTRY.copy()
    yield
    InterfaceRegistry.INTERFACE_REGISTRY = original


@pytest.mark.unit
def test_list_registered_namespaces_returns_all_keys():
    extra_key = "swarmauri.tests"
    InterfaceRegistry.INTERFACE_REGISTRY[extra_key] = None

    namespaces = InterfaceRegistry.list_registered_namespaces()

    assert extra_key in namespaces
