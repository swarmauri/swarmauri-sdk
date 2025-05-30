#!/usr/bin/env python3
"""Crash recovery benchmark for PT-6."""
from __future__ import annotations

import os
import subprocess
import sys
import time
from prometheus_client import Gauge, start_http_server, REGISTRY, exposition

RECOVERY_TIME = Gauge("crash_recovery_seconds", "Time to recover crashed task")


def main() -> None:
    """Simulate crash and recovery."""
    port = int(os.getenv("PROM_PORT", "8000"))
    metrics_file = os.getenv("METRICS_FILE")
    start_http_server(port)

    t0 = time.perf_counter()
    proc = subprocess.Popen([sys.executable, "-c", "import time; time.sleep(0.2)"])
    time.sleep(0.1)
    proc.kill()
    subprocess.Popen([sys.executable, "-c", "pass"]).wait()
    elapsed = time.perf_counter() - t0
    RECOVERY_TIME.set(elapsed)

    if metrics_file:
        metrics = exposition.generate_latest(REGISTRY).decode()
        with open(metrics_file, "w", encoding="utf-8") as fh:
            fh.write(metrics)


if __name__ == "__main__":
    main()
