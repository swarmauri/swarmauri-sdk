"""Benchmark Tigrbl request->response throughput for a simple runtime route.

This benchmark uses an in-process ASGI transport (httpx.ASGITransport) to
measure framework/runtime overhead deterministically without network jitter.
"""

from __future__ import annotations

import argparse
import asyncio
import time

import httpx
from tigrbl import TigrblApp, TigrblRouter


def build_app() -> TigrblApp:
    app = TigrblApp()
    router = TigrblRouter()

    async def ping(_request):
        return {"ok": True}

    router.add_route("/ping", ping, methods=["GET"])
    app.include_router(router)
    return app


async def _run_benchmark(*, iterations: int, warmup: int) -> tuple[float, float]:
    app = build_app()
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        for _ in range(warmup):
            response = await client.get("/ping")
            if response.status_code != 200:
                raise RuntimeError(
                    f"Warmup request failed with status {response.status_code}: {response.text}"
                )

        started = time.perf_counter()
        for _ in range(iterations):
            response = await client.get("/ping")
            if response.status_code != 200:
                raise RuntimeError(
                    f"Benchmark request failed with status {response.status_code}: {response.text}"
                )
        elapsed = time.perf_counter() - started

    return iterations / elapsed, elapsed


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--iterations", type=int, default=8000)
    parser.add_argument("--warmup", type=int, default=1000)
    parser.add_argument(
        "--baseline-ops-per-sec",
        type=float,
        default=None,
        help="Optional baseline ops/sec value to compare against.",
    )
    args = parser.parse_args()

    ops_per_sec, elapsed = asyncio.run(
        _run_benchmark(iterations=args.iterations, warmup=args.warmup)
    )

    print(f"ops_per_sec={ops_per_sec:.2f}")
    print(f"total_execution_time_sec={elapsed:.6f}")

    if args.baseline_ops_per_sec is not None:
        delta = (
            (ops_per_sec - args.baseline_ops_per_sec) / args.baseline_ops_per_sec
        ) * 100
        print(f"delta_percent_vs_baseline={delta:.2f}")


if __name__ == "__main__":
    main()
