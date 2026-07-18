import pytest

from swarmauri.interface_registry import InterfaceRegistry
from swarmauri_base.agents.AgentBase import AgentBase
from swarmauri_base.key_providers.KeyProviderBase import KeyProviderBase


@pytest.fixture(autouse=True)
def restore_interfaces():
    original = InterfaceRegistry.INTERFACE_REGISTRY.copy()
    yield
    InterfaceRegistry.INTERFACE_REGISTRY = original


@pytest.mark.unit
def test_get_registered_interface():
    assert (
        InterfaceRegistry.get_interface_for_resource("swarmauri.agents")
        is AgentBase
    )


@pytest.mark.unit
def test_get_interface_invalid_raises():
    with pytest.raises(KeyError):
        InterfaceRegistry.get_interface_for_resource("swarmauri.invalid")


@pytest.mark.unit
def test_register_and_unregister_interface():
    InterfaceRegistry.register_interface("swarmauri.tests", AgentBase)
    assert (
        InterfaceRegistry.get_interface_for_resource("swarmauri.tests")
        is AgentBase
    )
    InterfaceRegistry.unregister_interface("swarmauri.tests")
    assert InterfaceRegistry.INTERFACE_REGISTRY["swarmauri.tests"] is None


@pytest.mark.unit
def test_get_key_provider_interface():
    assert (
        InterfaceRegistry.get_interface_for_resource("swarmauri.key_providers")
        is KeyProviderBase
    )


@pytest.mark.unit
def test_get_retriever_interface():
    from swarmauri_base.retrievers.RetrieverBase import RetrieverBase

    assert (
        InterfaceRegistry.get_interface_for_resource("swarmauri.retrievers")
        is RetrieverBase
    )


@pytest.mark.unit
def test_get_video_lipsync_interface():
    from swarmauri_base.video_lipsync.LipSyncBase import LipSyncBase

    assert (
        InterfaceRegistry.get_interface_for_resource("swarmauri.video_lipsync")
        is LipSyncBase
    )
