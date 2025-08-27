from jollof.plugin_manager import PluginManager
from .dummy_plugins import ExamplePlugin


def test_registration_performance(benchmark):
    pm = PluginManager(domain="perf")

    def _register():
        for i in range(100):
            pm.register("bench", f"Plugin{i}", ExamplePlugin)

    benchmark(_register)
