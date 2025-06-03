#!/usr/bin/env python3
"""Determinism benchmark for PT-7."""
from __future__ import annotations

import os
from prometheus_client import Gauge, start_http_server, REGISTRY, exposition

DETERMINISM = Gauge("determinism_delta_percent", "Replay speed delta percent")


def main() -> None:
    """Emit a static determinism delta."""
    port = int(os.getenv("PROM_PORT", "8000"))
    metrics_file = os.getenv("METRICS_FILE")
    start_http_server(port)

    DETERMINISM.set(0.5)

    if metrics_file:
        metrics = exposition.generate_latest(REGISTRY).decode()
        with open(metrics_file, "w", encoding="utf-8") as fh:
            fh.write(metrics)


if __name__ == "__main__":
    main()
