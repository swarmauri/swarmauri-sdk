#!/usr/bin/env python3
"""Worker cold-start latency benchmark for PT-2."""
from __future__ import annotations

import os
import subprocess
import sys
import time
from prometheus_client import Gauge, start_http_server, REGISTRY, exposition

COLD_START = Gauge("worker_cold_start_seconds", "Worker cold start latency in seconds")


def main() -> None:
    """Measure process spawn time."""
    port = int(os.getenv("PROM_PORT", "8000"))
    metrics_file = os.getenv("METRICS_FILE")
    start_http_server(port)

    t0 = time.perf_counter()
    subprocess.run([sys.executable, "-c", "pass"], check=True)
    elapsed = time.perf_counter() - t0
    COLD_START.set(elapsed)

    if metrics_file:
        metrics = exposition.generate_latest(REGISTRY).decode()
        with open(metrics_file, "w", encoding="utf-8") as fh:
            fh.write(metrics)


if __name__ == "__main__":
    main()
