import importlib
import random
import string
import sys
import time
import types

from importlib.metadata import EntryPoint

from swarmauri.plugin_citizenship_registry import PluginCitizenshipRegistry
from swarmauri.plugin_manager import invalidate_entry_point_cache


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
        except (ModuleNotFoundError, ImportError):
            continue
        PluginCitizenshipRegistry.add_to_registry("first", resource_path, module_path)
    registration_time = time.perf_counter() - start

    PluginCitizenshipRegistry.FIRST_CLASS_REGISTRY = original_registry

    print(
        f"Startup: {startup_time:.4f}s, First-class registration: {registration_time:.4f}s"
    )

    assert startup_time >= 0
    assert registration_time >= 0


def test_namespace_startup_and_registration_of_random_classes():
    start = time.perf_counter()
    importlib.import_module("swarmauri")
    startup_time = time.perf_counter() - start

    PluginCitizenshipRegistry.SECOND_CLASS_REGISTRY.clear()
    PluginCitizenshipRegistry.THIRD_CLASS_REGISTRY.clear()
    invalidate_entry_point_cache()

    def _create_dummy_plugin(class_name: str) -> str:
        module_name = f"_dummy_plugin_{class_name}"
        module = types.ModuleType(module_name)
        cls = type(class_name, (), {})
        setattr(module, class_name, cls)
        sys.modules[module_name] = module
        ep = EntryPoint(
            name=class_name,
            value=f"{module_name}:{class_name}",
            group="swarmauri.plugins",
        )
        PluginCitizenshipRegistry.register_third_class_plugin(ep, module_name)
        return module_name

    names = [
        "Dummy" + "".join(random.choices(string.ascii_letters, k=8)) for _ in range(10)
    ]

    start = time.perf_counter()
    module_names = [_create_dummy_plugin(name) for name in names]
    registration_time = time.perf_counter() - start

    start = time.perf_counter()
    for name in names:
        importlib.import_module(f"swarmauri.plugins.{name}")
    import_time = time.perf_counter() - start

    print(
        f"Startup: {startup_time:.4f}s, Register10: {registration_time:.4f}s, "
        f"Import10: {import_time:.4f}s",
    )

    assert startup_time >= 0
    assert registration_time >= 0
    assert import_time >= 0

    for name, module_name in zip(names, module_names):
        sys.modules.pop(module_name, None)
        sys.modules.pop(f"swarmauri.plugins.{name}", None)
    PluginCitizenshipRegistry.THIRD_CLASS_REGISTRY.clear()
    PluginCitizenshipRegistry.SECOND_CLASS_REGISTRY.clear()


if __name__ == "__main__":
    test_startup_and_first_class_registration_performance()
