import importlib
import random
import time

from swarmauri.plugin_manager import (
    get_entry_points,
    invalidate_entry_point_cache,
    process_plugin,
)
from swarmauri.plugin_citizenship_registry import PluginCitizenshipRegistry


def test_startup_and_registration_performance():
    start = time.perf_counter()
    importlib.import_module("swarmauri")
    startup_time = time.perf_counter() - start

    PluginCitizenshipRegistry.SECOND_CLASS_REGISTRY.clear()
    PluginCitizenshipRegistry.THIRD_CLASS_REGISTRY.clear()
    invalidate_entry_point_cache()

    entry_points = [ep for eps in get_entry_points().values() for ep in eps]
    sample_size = min(5, len(entry_points))
    random.seed(0)
    selected = random.sample(entry_points, sample_size)

    start = time.perf_counter()
    for ep in selected:
        process_plugin(ep)
    registration_time = time.perf_counter() - start

    print(
        f"Startup: {startup_time:.4f}s, Register 5: {registration_time:.4f}s",
    )

    assert startup_time >= 0
    assert registration_time >= 0


if __name__ == "__main__":
    test_startup_and_registration_performance()
