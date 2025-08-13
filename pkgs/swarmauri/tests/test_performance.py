import importlib
import time

from swarmauri.plugin_manager import (
    discover_and_register_plugins,
    invalidate_entry_point_cache,
)
from swarmauri.plugin_citizenship_registry import PluginCitizenshipRegistry


def test_startup_and_registration_performance():
    start = time.perf_counter()
    importlib.import_module("swarmauri")
    startup_time = time.perf_counter() - start

    PluginCitizenshipRegistry.SECOND_CLASS_REGISTRY.clear()
    PluginCitizenshipRegistry.THIRD_CLASS_REGISTRY.clear()
    invalidate_entry_point_cache()
    start = time.perf_counter()
    discover_and_register_plugins()
    registration_time = time.perf_counter() - start

    PluginCitizenshipRegistry.SECOND_CLASS_REGISTRY.clear()
    PluginCitizenshipRegistry.THIRD_CLASS_REGISTRY.clear()
    invalidate_entry_point_cache()
    start = time.perf_counter()
    discover_and_register_plugins()
    rebuild_time = time.perf_counter() - start

    print(
        f"Startup: {startup_time:.4f}s, Register: {registration_time:.4f}s, "
        f"Rebuild: {rebuild_time:.4f}s",
    )

    assert startup_time >= 0
    assert registration_time >= 0
    assert rebuild_time >= 0


if __name__ == "__main__":
    test_startup_and_registration_performance()
