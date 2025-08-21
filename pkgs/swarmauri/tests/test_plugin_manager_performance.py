import time
import importlib

from swarmauri.plugin_manager import (
    discover_and_register_plugins,
    invalidate_entry_point_cache,
)
from swarmauri.plugin_citizenship_registry import PluginCitizenshipRegistry


def _reset_registries():
    PluginCitizenshipRegistry.FIRST_CLASS_REGISTRY = {}
    PluginCitizenshipRegistry.SECOND_CLASS_REGISTRY = {}
    PluginCitizenshipRegistry.THIRD_CLASS_REGISTRY = {}


def test_discovery_registers_plugins():
    _reset_registries()
    invalidate_entry_point_cache()
    discover_and_register_plugins()
    registry = PluginCitizenshipRegistry.total_registry()
    assert "swarmauri.vector_stores.Doc2VecVectorStore" in registry


def test_discovery_caching_speed():
    _reset_registries()
    invalidate_entry_point_cache()
    start = time.perf_counter()
    discover_and_register_plugins()
    first = time.perf_counter() - start

    _reset_registries()
    invalidate_entry_point_cache()
    start = time.perf_counter()
    discover_and_register_plugins()
    second = time.perf_counter() - start

    assert second <= first * 1.1


def test_plugin_import_time():
    start = time.perf_counter()
    importlib.import_module("swarmauri_vectorstore_doc2vec")
    elapsed = time.perf_counter() - start
    assert elapsed < 5
