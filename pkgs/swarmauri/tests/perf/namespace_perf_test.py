import importlib
import sys
import time
import types

import pytest

@pytest.mark.perf
def test_namespace_import_performance(monkeypatch):
    """Import the swarmauri namespace package within an acceptable time."""
    yaml_stub = types.SimpleNamespace(
        safe_load=lambda data: {},
        dump=lambda data, default_flow_style=False: "",
        YAMLError=Exception,
    )
    monkeypatch.setitem(sys.modules, "yaml", yaml_stub)

    interface_stub = types.ModuleType("swarmauri.interface_registry")

    class InterfaceRegistry:
        INTERFACE_REGISTRY = {"swarmauri.plugins": None}

    interface_stub.InterfaceRegistry = InterfaceRegistry
    monkeypatch.setitem(sys.modules, "swarmauri.interface_registry", interface_stub)

    plugin_manager_stub = types.ModuleType("swarmauri.plugin_manager")
    plugin_manager_stub.discover_and_register_plugins = lambda: None
    monkeypatch.setitem(sys.modules, "swarmauri.plugin_manager", plugin_manager_stub)

    start = time.perf_counter()
    importlib.import_module("swarmauri")
    duration = time.perf_counter() - start

    assert duration < 0.5

@pytest.mark.perf
def test_importer_find_spec_performance(monkeypatch):
    """Ensure SwarmauriImporter.find_spec executes quickly."""
    yaml_stub = types.SimpleNamespace(
        safe_load=lambda data: {},
        dump=lambda data, default_flow_style=False: "",
        YAMLError=Exception,
    )
    monkeypatch.setitem(sys.modules, "yaml", yaml_stub)

    interface_stub = types.ModuleType("swarmauri.interface_registry")

    class InterfaceRegistry:
        INTERFACE_REGISTRY = {"swarmauri.plugins": None}

    interface_stub.InterfaceRegistry = InterfaceRegistry
    monkeypatch.setitem(sys.modules, "swarmauri.interface_registry", interface_stub)

    plugin_manager_stub = types.ModuleType("swarmauri.plugin_manager")
    plugin_manager_stub.discover_and_register_plugins = lambda: None
    monkeypatch.setitem(sys.modules, "swarmauri.plugin_manager", plugin_manager_stub)

    from swarmauri.importer import SwarmauriImporter
    from swarmauri.plugin_citizenship_registry import PluginCitizenshipRegistry

    PluginCitizenshipRegistry.THIRD_CLASS_REGISTRY["swarmauri.plugins.math"] = "math"

    importer = SwarmauriImporter()

    start = time.perf_counter()
    for _ in range(1000):
        importer.find_spec("swarmauri.plugins.math")
    duration = time.perf_counter() - start

    assert duration < 0.1
