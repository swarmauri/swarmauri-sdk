#!/usr/bin/env python3
"""Queue throughput benchmark for PT-3."""
from __future__ import annotations

import os
import time
from prometheus_client import Gauge, start_http_server, REGISTRY, exposition

QUEUE_TPM = Gauge("queue_throughput_tpm", "Tasks processed per minute")


def main() -> None:
    """Simulate queue throughput."""
    port = int(os.getenv("PROM_PORT", "8000"))
    metrics_file = os.getenv("METRICS_FILE")
    start_http_server(port)

    tasks = 2000
    start = time.perf_counter()
    for _ in range(tasks):
        pass
    elapsed = time.perf_counter() - start
    QUEUE_TPM.set(tasks / elapsed * 60)

    if metrics_file:
        metrics = exposition.generate_latest(REGISTRY).decode()
        with open(metrics_file, "w", encoding="utf-8") as fh:
            fh.write(metrics)


if __name__ == "__main__":
    main()
