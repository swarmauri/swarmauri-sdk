import pytest

from swarmauri.plugin_citizenship_registry import PluginCitizenshipRegistry


@pytest.fixture(autouse=True)
def restore_registry():
    """Restore plugin registries after each test."""
    first = PluginCitizenshipRegistry.FIRST_CLASS_REGISTRY.copy()
    second = PluginCitizenshipRegistry.SECOND_CLASS_REGISTRY.copy()
    third = PluginCitizenshipRegistry.THIRD_CLASS_REGISTRY.copy()
    yield
    PluginCitizenshipRegistry.FIRST_CLASS_REGISTRY = first
    PluginCitizenshipRegistry.SECOND_CLASS_REGISTRY = second
    PluginCitizenshipRegistry.THIRD_CLASS_REGISTRY = third


@pytest.mark.unit
def test_add_and_remove_entry():
    PluginCitizenshipRegistry.add_to_registry(
        "first", "swarmauri.agents.TestAgent", "tests.test_module.TestAgent"
    )
    assert (
        PluginCitizenshipRegistry.FIRST_CLASS_REGISTRY["swarmauri.agents.TestAgent"]
        == "tests.test_module.TestAgent"
    )

    PluginCitizenshipRegistry.remove_from_registry(
        "first", "swarmauri.agents.TestAgent"
    )
    assert (
        "swarmauri.agents.TestAgent"
        not in PluginCitizenshipRegistry.FIRST_CLASS_REGISTRY
    )


@pytest.mark.unit
def test_add_duplicate_entry_noop():
    PluginCitizenshipRegistry.add_to_registry(
        "third", "swarmauri.plugins.sample", "math"
    )
    # Duplicate addition should be ignored without raising an error
    PluginCitizenshipRegistry.add_to_registry(
        "third", "swarmauri.plugins.sample", "math"
    )
    assert (
        PluginCitizenshipRegistry.THIRD_CLASS_REGISTRY["swarmauri.plugins.sample"]
        == "math"
    )


@pytest.mark.unit
def test_update_and_delete_entry():
    PluginCitizenshipRegistry.add_to_registry(
        "second", "swarmauri.chains.TestChain", "pkg.Chain"
    )
    PluginCitizenshipRegistry.update_entry(
        "second", "swarmauri.chains.TestChain", "pkg.NewChain"
    )
    assert (
        PluginCitizenshipRegistry.SECOND_CLASS_REGISTRY["swarmauri.chains.TestChain"]
        == "pkg.NewChain"
    )

    PluginCitizenshipRegistry.delete_entry("second", "swarmauri.chains.TestChain")
    assert (
        "swarmauri.chains.TestChain"
        not in PluginCitizenshipRegistry.SECOND_CLASS_REGISTRY
    )
