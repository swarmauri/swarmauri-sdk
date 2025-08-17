import importlib, sys
import pytest
from swarmauri import plugin_manager, PluginCitizenshipRegistry

@pytest.mark.perf
@pytest.mark.parametrize("num_plugins", [0, 10, 50, 100])
def test_plugin_discovery_performance(num_plugins, benchmark):
    # Setup: monkeypatch plugin discovery to simulate `num_plugins` plugins
    fake_eps = make_fake_entry_points(num_plugins)  # our helper to create dummy EntryPoint list
    plugin_manager.invalidate_entry_point_cache()        # Clear any cached entry points:contentReference[oaicite:10]{index=10}
    monkeypatch = pytest.MonkeyPatch()
    monkeypatch.setattr(plugin_manager, "get_entry_points", lambda prefix="swarmauri.": fake_eps)
    
    # Benchmark the discovery+registration process
    def do_discovery():
        plugin_manager.discover_and_register_plugins()  # this calls process_plugin on each fake entry
    time_taken = benchmark(do_discovery)
    
    # Teardown: reset global state for next test
    PluginCitizenshipRegistry.reset_all()    # new method to clear registries
    plugin_manager.invalidate_entry_point_cache()
    for mod in list(sys.modules):
        if mod.startswith("swarmauri.") and mod not in ("swarmauri", "swarmauri.importer"):
            sys.modules.pop(mod)  # remove loaded plugin modules
    monkeypatch.undo()
    
    # (Optionally, assert something about time_taken or that registry size == num_plugins, etc.)
