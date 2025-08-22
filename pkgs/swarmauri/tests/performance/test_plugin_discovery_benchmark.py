import importlib
from swarmauri.plugin_manager import (
    invalidate_entry_point_cache,
    discover_and_register_plugins,
)
from swarmauri.plugin_citizenship_registry import PluginCitizenshipRegistry

FIRST_CLASS_PLUGINS = [
    "swarmauri.agents.QAAgent",
    "swarmauri.llms.OpenAIModel",
    "swarmauri.chains.CallableChain",
]


def import_first_class_plugins():
    invalidate_entry_point_cache()
    PluginCitizenshipRegistry.SECOND_CLASS_REGISTRY.clear()
    PluginCitizenshipRegistry.THIRD_CLASS_REGISTRY.clear()
    discover_and_register_plugins(force=True)
    for module in FIRST_CLASS_PLUGINS:
        importlib.import_module(module)


def test_first_class_plugin_imports(benchmark):
    benchmark(import_first_class_plugins)


def import_missing_plugin():
    invalidate_entry_point_cache()
    PluginCitizenshipRegistry.SECOND_CLASS_REGISTRY.clear()
    PluginCitizenshipRegistry.THIRD_CLASS_REGISTRY.clear()
    discover_and_register_plugins(force=True)
    try:
        importlib.import_module("swarmauri.agents.DoesNotExist")
    except Exception:
        pass


def test_missing_plugin_import(benchmark):
    benchmark(import_missing_plugin)
