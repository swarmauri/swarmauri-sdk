#!/usr/bin/env python3
"""Idle cost benchmark for PT-5."""
from __future__ import annotations

import os
from prometheus_client import Gauge, start_http_server, REGISTRY, exposition

IDLE_COST = Gauge("idle_cost_hours", "Billable pod-hours during idle period")


def main() -> None:
    """Emit a static idle cost value."""
    port = int(os.getenv("PROM_PORT", "8000"))
    metrics_file = os.getenv("METRICS_FILE")
    start_http_server(port)

    IDLE_COST.set(0.1)

    if metrics_file:
        metrics = exposition.generate_latest(REGISTRY).decode()
        with open(metrics_file, "w", encoding="utf-8") as fh:
            fh.write(metrics)


if __name__ == "__main__":
    main()
