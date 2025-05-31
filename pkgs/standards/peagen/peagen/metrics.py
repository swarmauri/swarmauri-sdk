"""Prometheus metrics for Peagen workers and spawners."""

from __future__ import annotations

from typing import Iterable

from prometheus_client import Counter, Gauge, Histogram, start_http_server

__all__ = [
    "start_metrics_server",
    "worker_task_total",
    "worker_runtime_seconds",
    "worker_exit_reason",
    "warm_spawner_live_workers",
    "queue_pending_total",
]

worker_task_total = Counter(
    "worker_task_total", "Count of tasks processed", ["status"]
)
worker_runtime_seconds = Histogram(
    "worker_runtime_seconds", "Task runtime in seconds"
)
worker_exit_reason = Counter(
    "worker_exit_reason", "Reason worker exited", ["reason"]
)
warm_spawner_live_workers = Gauge(
    "warm_spawner_live_workers", "Number of active worker processes"
)
queue_pending_total = Gauge(
    "queue_pending_total", "Tasks waiting in queue", ["kind"]
)


_metrics_started = False

def start_metrics_server(port: int = 8000) -> None:
    """Start the Prometheus metrics HTTP exporter."""
    global _metrics_started
    if not _metrics_started:
        start_http_server(port)
        _metrics_started = True

