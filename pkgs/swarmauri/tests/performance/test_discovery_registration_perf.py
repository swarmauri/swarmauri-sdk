# tests/perf/test_discovery_registration_perf.py
from __future__ import annotations

import time
import pytest

from swarmauri.plugin_manager import discover_and_register_plugins, reset_plugin_environment
from .utils import select_groups, build_grouped_fake_entry_points


@pytest.mark.perf
@pytest.mark.parametrize("models,plugins", [
    (5, 10),
    (5, 50),
    (10, 50),
    (10, 100),
    (20, 100),
    (20, 200),
])
@pytest.mark.parametrize("mode", ["class"])  # you can add "module" to cover module path as well
def test_discovery_and_registration_perf(models: int, plugins: int, mode: str):
    """
    Measures discovery+registration time with deterministic fake entry points.
    Wipes state before and after (via autouse fixture).
    """
    groups = select_groups(models)
    grouped_eps = build_grouped_fake_entry_points(groups, plugins, mode=mode)

    # Ensure a cold environment for this measurement.
    reset_plugin_environment(unload_prefixes=("swarmauri_test_plugins",))

    t0 = time.perf_counter()
    stats = discover_and_register_plugins(collect_stats=True, entry_points_override=grouped_eps)
    elapsed = time.perf_counter() - t0

    # Sanity checks
    assert stats is not None
    processed = stats.get("processed", 0)
    succeeded = stats.get("succeeded", 0)
    failed = stats.get("failed", 0)

    # With valid fake EPs, all should succeed.
    assert processed == plugins, f"processed={processed}, expected={plugins}"
    assert failed == 0, f"failed={failed}"
    assert succeeded == plugins, f"succeeded={succeeded}, expected={plugins}"

    # Log timing to stdout so CI artifacts capture it without extra plugins.
    fetch = stats.get("fetch_seconds", 0.0)
    process = stats.get("process_seconds", 0.0)
    print(
        f"[perf] models={models} plugins={plugins} mode={mode} "
        f"elapsed={elapsed:.6f}s fetch={fetch:.6f}s process={process:.6f}s"
    )
