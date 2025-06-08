import pytest

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
def test_get_external_module_path_returns_correct_path():
    PluginCitizenshipRegistry.THIRD_CLASS_REGISTRY["swarmauri.plugins.sample"] = "math"
    path = PluginCitizenshipRegistry.get_external_module_path("swarmauri.plugins.sample")
    assert path == "math"


@pytest.mark.unit
def test_list_registry_returns_specific_registry():
    PluginCitizenshipRegistry.SECOND_CLASS_REGISTRY["swarmauri.chains.Dummy"] = "pkg.Dummy"
    registry = PluginCitizenshipRegistry.list_registry("second")
    assert registry == {"swarmauri.chains.Dummy": "pkg.Dummy"}


@pytest.mark.unit
def test_total_registry_includes_all_classes():
    PluginCitizenshipRegistry.FIRST_CLASS_REGISTRY.clear()
    PluginCitizenshipRegistry.SECOND_CLASS_REGISTRY["swarmauri.chains.Dummy"] = "pkg.Dummy"
    PluginCitizenshipRegistry.THIRD_CLASS_REGISTRY["swarmauri.plugins.sample"] = "math"

    total = PluginCitizenshipRegistry.total_registry()

    expected = {
        "swarmauri.chains.Dummy": "pkg.Dummy",
        "swarmauri.plugins.sample": "math",
    }
    assert total == expected
