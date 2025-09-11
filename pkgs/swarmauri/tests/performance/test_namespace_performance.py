import os
import subprocess
import sys
from pathlib import Path

PKG_DIR = Path(__file__).resolve().parents[2]


def _run_perf_snippet(snippet: str) -> float:
    env = os.environ.copy()
    result = subprocess.run(
        [sys.executable, "-c", snippet],
        capture_output=True,
        text=True,
        cwd=str(PKG_DIR),
        env=env,
        check=True,
    )
    return float(result.stdout.strip())


def test_namespace_startup_time():
    code = """
import time
start = time.perf_counter()
import swarmauri  # noqa: F401
print(time.perf_counter() - start)
"""
    duration = _run_perf_snippet(code)
    assert duration < 5.0, f"Startup took too long: {duration:.2f}s"


def test_class_registration_time():
    code = """
import time
import swarmauri  # noqa: F401
from swarmauri.plugin_manager import invalidate_entry_point_cache, discover_and_register_plugins
invalidate_entry_point_cache()
start = time.perf_counter()
discover_and_register_plugins()
print(time.perf_counter() - start)
"""
    duration = _run_perf_snippet(code)
    assert duration < 2.0, f"Registration took too long: {duration:.2f}s"
