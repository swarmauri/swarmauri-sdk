# tests/perf/conftest.py
import os
import pytest

@pytest.fixture(autouse=True)
def _clean_state():
    # Disable auto-discovery for deterministic import timing.
    os.environ.setdefault("SWARMAURI_DISABLE_AUTO_DISCOVERY", "1")
    # Keep stats logging off unless you explicitly enable it in a test.
    os.environ.setdefault("SWARMAURI_DISCOVERY_STATS", "0")

    # Lazy import to ensure env vars are set first.
    from swarmauri.plugin_manager import reset_plugin_environment

    # Clean before
    reset_plugin_environment(unload_prefixes=("swarmauri_test_plugins",))
    yield
    # Clean after
    reset_plugin_environment(unload_prefixes=("swarmauri_test_plugins",))
