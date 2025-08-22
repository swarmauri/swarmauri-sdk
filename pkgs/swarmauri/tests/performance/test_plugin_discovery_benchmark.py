from swarmauri.plugin_manager import (
    discover_and_register_plugins,
    invalidate_entry_point_cache,
)
from importlib.metadata import EntryPoint


def test_discovery_perf_happy(benchmark):
    def run():
        invalidate_entry_point_cache()
        discover_and_register_plugins()

    benchmark(run)


def test_discovery_perf_worst_case(benchmark, monkeypatch):
    fake_ep = EntryPoint(
        name="missing", value="missing.module:attr", group="swarmauri.agents"
    )

    def fake_get_entry_points(prefix: str = "swarmauri."):
        return {"agents": [fake_ep]}

    monkeypatch.setattr(
        "swarmauri.plugin_manager.get_entry_points", fake_get_entry_points
    )

    def run():
        invalidate_entry_point_cache()
        try:
            discover_and_register_plugins()
        except Exception:
            pass

    benchmark(run)
