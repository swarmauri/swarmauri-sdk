import importlib.machinery
import pytest

from swarmauri.importer import SwarmauriImporter
from swarmauri.plugin_citizenship_registry import PluginCitizenshipRegistry


@pytest.fixture(autouse=True)
def restore_registry():
    third = PluginCitizenshipRegistry.THIRD_CLASS_REGISTRY.copy()
    yield
    PluginCitizenshipRegistry.THIRD_CLASS_REGISTRY = third


@pytest.mark.unit
def test_find_spec_for_registered_module():
    PluginCitizenshipRegistry.THIRD_CLASS_REGISTRY["swarmauri.plugins.math"] = "math"
    importer = SwarmauriImporter()
    spec = importer.find_spec("swarmauri.plugins.math")
    assert isinstance(spec, importlib.machinery.ModuleSpec)
