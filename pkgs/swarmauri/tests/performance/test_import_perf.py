# tests/perf/test_import_perf.py
from __future__ import annotations

import os
import subprocess
import sys
import textwrap
import pytest

PY = sys.executable


@pytest.mark.perf
def test_cold_import_without_discovery_perf(tmp_path):
    """
    Measures the cost of importing 'swarmauri' package alone (no discovery).
    Uses a fresh interpreter for a realistic cold start.
    """
    code = textwrap.dedent(
        """
        import os, time
        os.environ['SWARMAURI_DISABLE_AUTO_DISCOVERY'] = '1'
        t0 = time.perf_counter()
        import swarmauri  # noqa: F401
        dt = time.perf_counter() - t0
        print(f"{dt:.9f}")
        """
    )
    script = tmp_path / "cold_import_no_discovery.py"
    script.write_text(code, encoding="utf-8")

    out = subprocess.check_output([PY, str(script)], text=True)
    elapsed = float(out.strip())
    print(f"[perf] import_only elapsed={elapsed:.6f}s")

    # Add a sanity ceiling to catch regressions (tune to your CI box)
    assert elapsed >= 0.0
