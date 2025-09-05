import time

from swarmauri.plugin_citizenship_registry import PluginCitizenshipRegistry
from swarmauri.plugin_manager import (
    discover_and_register_plugins,
    invalidate_entry_point_cache,
)


def test_discovery_cache_performance_happy_vs_worst():
    """Verify caching speeds up discovery (>75%) from worst to happy path."""
    PluginCitizenshipRegistry.SECOND_CLASS_REGISTRY.clear()
    PluginCitizenshipRegistry.THIRD_CLASS_REGISTRY.clear()
    original_first = PluginCitizenshipRegistry.FIRST_CLASS_REGISTRY.copy()
    PluginCitizenshipRegistry.FIRST_CLASS_REGISTRY.clear()
    invalidate_entry_point_cache()

    start = time.perf_counter()
    discover_and_register_plugins()
    uncached = time.perf_counter() - start

    start = time.perf_counter()
    discover_and_register_plugins()
    cached = time.perf_counter() - start

    assert cached <= uncached * 0.25

    PluginCitizenshipRegistry.FIRST_CLASS_REGISTRY = original_first
