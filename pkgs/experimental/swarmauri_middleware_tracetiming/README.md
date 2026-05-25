![Swarmauri Logo](https://github.com/swarmauri/swarmauri-sdk/blob/3d4d1cfa949399d7019ae9d8f296afba773dfb7f/assets/swarmauri.brand.theme.svg)

<p align="center">
    <a href="https://pypi.org/project/swarmauri_middleware_tracetiming/">
        <img src="https://img.shields.io/pypi/dm/swarmauri_middleware_tracetiming" alt="PyPI - Downloads"/></a>
    <a href="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/swarmauri_middleware_tracetiming/">
        <img alt="Hits" src="https://hits.sh/github.com/swarmauri/swarmauri-sdk/tree/master/pkgs/experimental/swarmauri_middleware_tracetiming.svg"/></a>
    <a href="https://pypi.org/project/swarmauri_middleware_tracetiming/">
        <img src="https://img.shields.io/pypi/pyversions/swarmauri_middleware_tracetiming" alt="PyPI - Python Version"/></a>
    <a href="https://pypi.org/project/swarmauri_middleware_tracetiming/">
        <img src="https://img.shields.io/pypi/l/swarmauri_middleware_tracetiming" alt="PyPI - License"/></a>
    <a href="https://pypi.org/project/swarmauri_middleware_tracetiming/">
        <img src="https://img.shields.io/pypi/v/swarmauri_middleware_tracetiming?label=swarmauri_middleware_tracetiming&color=green" alt="PyPI - swarmauri_middleware_tracetiming"/></a>
</p>

---

# Swarmauri Middleware TraceTiming

`TraceTimingMiddleware` adds distributed tracing and latency metadata to ASGI responses using Swarmauri's middleware contract.

## Features

- Reads incoming `traceparent` / `tracestate` headers and generates a compliant `traceparent` when missing.
- Appends compact `Server-Timing` metrics using `app;dur=...` and optional `edge;dur=...`.
- Adds `Timing-Allow-Origin` for browser visibility.
- Guarantees outgoing response headers include propagated tracing context.
- Implements `MiddlewareBase` hooks (`on_scope`, `on_send`) for native Swarmauri middleware chaining.

## Installation

```bash
# with uv
uv add swarmauri_middleware_tracetiming

# with pip
pip install swarmauri_middleware_tracetiming
```

## Usage

```python
from fastapi import FastAPI
from swarmauri_middleware_tracetiming import TraceTimingMiddleware

app = FastAPI()

# Optionally inject your own edge duration calculator
edge_ms_getter = lambda scope: 12.5

app.add_middleware(
    TraceTimingMiddleware,
    edge_ms_getter=edge_ms_getter,
    timing_allow_origin="*",
)
```

Expected behavior per request:

1. Extracts or creates `traceparent`.
2. Stores trace and timing data in `scope` for lifecycle-safe processing.
3. Writes `server-timing`, `timing-allow-origin`, and trace headers on `http.response.start`.

## Compatibility

- Python 3.10, 3.11, and 3.12.
- Works in ASGI middleware stacks that support Swarmauri `MiddlewareBase` plugins.

## Want to help?

If you want to contribute to swarmauri-sdk, read [contributing.md](https://github.com/swarmauri/swarmauri-sdk/blob/master/contributing.md).
