import pytest
from importlib.metadata import EntryPoint

from swarmauri.plugin_manager import determine_plugin_citizenship
from swarmauri.plugin_citizenship_registry import PluginCitizenshipRegistry


@pytest.fixture(autouse=True)
def restore_registry():
    first = PluginCitizenshipRegistry.FIRST_CLASS_REGISTRY.copy()
    second = PluginCitizenshipRegistry.SECOND_CLASS_REGISTRY.copy()
    third = PluginCitizenshipRegistry.THIRD_CLASS_REGISTRY.copy()
    yield
    PluginCitizenshipRegistry.FIRST_CLASS_REGISTRY = first
    PluginCitizenshipRegistry.SECOND_CLASS_REGISTRY = second
    PluginCitizenshipRegistry.THIRD_CLASS_REGISTRY = third


@pytest.mark.unit
def test_third_class_detection():
    ep = EntryPoint(name="Dummy", value="pkg.module:Dummy", group="swarmauri.plugins")
    assert determine_plugin_citizenship(ep) == "third"


@pytest.mark.unit
def test_first_class_detection():
    ep = EntryPoint(
        name="DummyAgent", value="pkg.agent:DummyAgent", group="swarmauri.agents"
    )
    PluginCitizenshipRegistry.FIRST_CLASS_REGISTRY["swarmauri.agents.DummyAgent"] = (
        "pkg.agent:DummyAgent"
    )
    assert determine_plugin_citizenship(ep) == "first"


@pytest.mark.unit
def test_second_class_detection():
    ep = EntryPoint(
        name="CommunityAgent",
        value="pkg.agent:CommunityAgent",
        group="swarmauri.agents",
    )
    assert determine_plugin_citizenship(ep) == "second"


@pytest.mark.unit
def test_unrecognized_plugin():
    ep = EntryPoint(name="Unknown", value="pkg.unknown:Unknown", group="unknown.group")
    assert determine_plugin_citizenship(ep) is None
