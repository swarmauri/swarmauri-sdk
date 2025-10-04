from __future__ import annotations

from typing import Optional

# Try Prometheus; fallback to no-op counters/gauges/histograms
try:
    from prometheus_client import Counter, Histogram, Gauge, generate_latest
except Exception:  # pragma: no cover
    Counter = Histogram = Gauge = None
    def generate_latest():
        return b""

# Counters
REQUESTS_TOTAL = Counter("acme_requests_total", "Total ACME API requests", ["route", "method"]) if Counter else None
ORDERS_ISSUED_TOTAL = Counter("acme_orders_issued_total", "Total certificates issued via ACME") if Counter else None
CHALLENGES_VALID_TOTAL = Counter("acme_challenges_valid_total", "Total challenges validated successfully", ["type"]) if Counter else None
REVOCATIONS_TOTAL = Counter("acme_revocations_total", "Total certificate revocations") if Counter else None

# Histograms
DB_DURATION_SECONDS = Histogram("db_duration_seconds", "DB operation durations", buckets=[0.005,0.01,0.025,0.05,0.1,0.25,0.5,1,2,5]) if Histogram else None

# Gauges
ORDERS_PROCESSING = Gauge("acme_orders_processing", "Orders in processing state") if Gauge else None

def inc_request(route: str, method: str) -> None:
    if REQUESTS_TOTAL:
        REQUESTS_TOTAL.labels(route=route, method=method).inc()

def inc_order_issued() -> None:
    if ORDERS_ISSUED_TOTAL:
        ORDERS_ISSUED_TOTAL.inc()

def inc_challenge_valid(ctype: str) -> None:
    if CHALLENGES_VALID_TOTAL:
        CHALLENGES_VALID_TOTAL.labels(type=ctype).inc()

def inc_revocation() -> None:
    if REVOCATIONS_TOTAL:
        REVOCATIONS_TOTAL.inc()

def observe_db(seconds: float) -> None:
    if DB_DURATION_SECONDS:
        DB_DURATION_SECONDS.observe(seconds)

def set_orders_processing(value: int) -> None:
    if ORDERS_PROCESSING:
        ORDERS_PROCESSING.set(value)

def metrics_text() -> str:
    try:
        return generate_latest().decode("utf-8")
    except Exception:
        return ""
