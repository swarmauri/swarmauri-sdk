import importlib
import pytest

from swarmauri.plugin_manager import (
    discover_and_register_plugins,
    invalidate_entry_point_cache,
)
from swarmauri.plugin_citizenship_registry import PluginCitizenshipRegistry

PLUGINS = [
    "swarmauri_standard.tools.AdditionTool",
    "swarmauri_standard.tools.CalculatorTool",
    "swarmauri_standard.tools.CodeInterpreterTool",
]


def _import_plugins() -> None:
    for path in PLUGINS:
        importlib.import_module(path)


@pytest.mark.benchmark
def test_discovery_registration_fresh(benchmark) -> None:
    def run():
        invalidate_entry_point_cache()
        discover_and_register_plugins()
        _import_plugins()

    benchmark(run)
    assert PluginCitizenshipRegistry.resource_exists("swarmauri.tools.AdditionTool")


@pytest.mark.benchmark
def test_discovery_registration_cached(benchmark) -> None:
    invalidate_entry_point_cache()
    discover_and_register_plugins()
    _import_plugins()

    def run():
        discover_and_register_plugins()
        _import_plugins()

    benchmark(run)
    assert PluginCitizenshipRegistry.resource_exists("swarmauri.tools.AdditionTool")
