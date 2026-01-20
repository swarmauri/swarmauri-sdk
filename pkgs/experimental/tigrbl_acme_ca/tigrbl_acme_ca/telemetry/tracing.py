from __future__ import annotations

from contextlib import contextmanager

# Try to use OpenTelemetry if available; otherwise no-op.
try:
    from opentelemetry import trace
    from opentelemetry.sdk.trace import TracerProvider
    from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
    from opentelemetry.trace.propagation.tracecontext import (
        TraceContextTextMapPropagator,
    )
except Exception:  # pragma: no cover
    trace = None
    TracerProvider = None
    BatchSpanProcessor = None
    ConsoleSpanExporter = None
    TraceContextTextMapPropagator = None

_tracer = None


def setup_tracing(service_name: str = "tigrbl-acme-ca") -> None:
    global _tracer
    if trace is None or TracerProvider is None:
        _tracer = None
        return
    provider = TracerProvider()
    provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
    trace.set_tracer_provider(provider)
    _tracer = trace.get_tracer(service_name)


@contextmanager
def start_span(name: str):
    if _tracer is None:
        yield None
        return
    with _tracer.start_as_current_span(name) as span:
        try:
            yield span
        finally:
            pass


def inject_trace_headers(headers: dict) -> None:
    if TraceContextTextMapPropagator is None:
        return
    try:
        propagator = TraceContextTextMapPropagator()
        carrier = {}
        propagator.inject(carrier)
        headers.update(carrier)
    except Exception:
        pass


def record_exception(span, exc: Exception) -> None:
    if span is None:
        return
    try:
        span.record_exception(exc)
    except Exception:
        pass
