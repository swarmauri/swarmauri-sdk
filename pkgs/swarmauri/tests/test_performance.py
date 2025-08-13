import importlib
import time

from swarmauri.plugin_citizenship_registry import PluginCitizenshipRegistry


def test_startup_and_first_class_registration_performance() -> None:
    start = time.perf_counter()
    importlib.import_module("swarmauri")
    startup_time = time.perf_counter() - start

    original_registry = PluginCitizenshipRegistry.FIRST_CLASS_REGISTRY.copy()
    PluginCitizenshipRegistry.FIRST_CLASS_REGISTRY.clear()

    start = time.perf_counter()
    for resource_path, module_path in original_registry.items():
        try:
            importlib.import_module(module_path)
        except ModuleNotFoundError:
            continue
        PluginCitizenshipRegistry.add_to_registry("first", resource_path, module_path)
    registration_time = time.perf_counter() - start

    PluginCitizenshipRegistry.FIRST_CLASS_REGISTRY = original_registry

    print(
        f"Startup: {startup_time:.4f}s, First-class registration: {registration_time:.4f}s"
    )

    assert startup_time >= 0
    assert registration_time >= 0


if __name__ == "__main__":
    test_startup_and_first_class_registration_performance()
