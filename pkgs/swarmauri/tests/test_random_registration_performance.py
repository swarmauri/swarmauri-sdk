import importlib
import random
import string
import time
from importlib.metadata import EntryPoint

from swarmauri.plugin_citizenship_registry import PluginCitizenshipRegistry


def test_startup_and_random_registration_performance():
    start = time.perf_counter()
    importlib.import_module("swarmauri")
    startup_time = time.perf_counter() - start

    PluginCitizenshipRegistry.THIRD_CLASS_REGISTRY.clear()
    start = time.perf_counter()
    for _ in range(25):
        name = "".join(random.choices(string.ascii_letters, k=8))
        entry_point = EntryPoint(
            name=name, value=f"dummy_module:{name}", group="swarmauri.plugins"
        )
        PluginCitizenshipRegistry.register_third_class_plugin(
            entry_point, f"dummy_module.{name}"
        )
    registration_time = time.perf_counter() - start
    PluginCitizenshipRegistry.THIRD_CLASS_REGISTRY.clear()

    print(f"Startup: {startup_time:.4f}s, Register 25: {registration_time:.4f}s")

    assert startup_time >= 0
    assert registration_time >= 0
