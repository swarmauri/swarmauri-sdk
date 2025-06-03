#!/usr/bin/env python3
"""Bubble sort benchmark for PT-1 and PT-4."""
from __future__ import annotations

import os
import random
import time
from prometheus_client import Gauge, Counter, start_http_server, REGISTRY, exposition

BEST_SPEED_MS = Gauge("evo_best_speed_ms", "Speed of champion variant in ms")
TOKENS_TOTAL = Counter("llm_tokens_total", "Total LLM tokens used")
TOKEN_EFFICIENCY = Gauge("token_efficiency", "Tokens per 1 percent speed gain")


def _bubble_sort(data: list[float]) -> None:
    """Sort the list in-place using bubble sort."""
    for i in range(len(data)):
        for j in range(len(data) - i - 1):
            if data[j] > data[j + 1]:
                data[j], data[j + 1] = data[j + 1], data[j]


def main() -> None:
    """Run the sorting workload and emit metrics."""
    port = int(os.getenv("PROM_PORT", "8000"))
    metrics_file = os.getenv("METRICS_FILE")
    start_http_server(port)

    baseline_ms = 1000.0
    best = float("inf")
    tokens = 0
    for _ in range(5):
        arr = [random.random() for _ in range(2000)]
        t0 = time.perf_counter()
        _bubble_sort(arr)
        elapsed = (time.perf_counter() - t0) * 1000
        best = min(best, elapsed)
        tokens += random.randint(100, 200)

    BEST_SPEED_MS.set(best)
    TOKENS_TOTAL.inc(tokens)
    improvement = max(baseline_ms - best, 1.0)
    percent = improvement / baseline_ms * 100
    TOKEN_EFFICIENCY.set(tokens / percent)

    if metrics_file:
        metrics = exposition.generate_latest(REGISTRY).decode()
        with open(metrics_file, "w", encoding="utf-8") as fh:
            fh.write(metrics)


if __name__ == "__main__":
    main()
