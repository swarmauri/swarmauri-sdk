from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from time import perf_counter
from typing import Any

import httpx

from tests.i9n.uvicorn_utils import run_uvicorn_in_task, stop_uvicorn_server
from tests.perf.helper_tigrbl_create_app import (
    create_tigrbl_app,
    initialize_tigrbl_app,
    tigrbl_create_path,
)


async def _run_request_response_benchmark(
    *, ops: int, warmup_ops: int
) -> dict[str, Any]:
    with TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "request_response.sqlite3"
        app = create_tigrbl_app(db_path)
        await initialize_tigrbl_app(app)
        base_url, server, task = await run_uvicorn_in_task(app)

        try:
            async with httpx.AsyncClient(base_url=base_url, timeout=20.0) as client:
                for _ in range(40):
                    ready = await client.get("/healthz")
                    if ready.status_code == 200:
                        break
                    await asyncio.sleep(0.05)

                for idx in range(warmup_ops):
                    response = await client.post(
                        tigrbl_create_path(), json={"name": f"warmup-{idx}"}
                    )
                    assert response.status_code in {200, 201}, response.text

                start = perf_counter()
                for idx in range(ops):
                    response = await client.post(
                        tigrbl_create_path(), json={"name": f"bench-{idx}"}
                    )
                    assert response.status_code in {200, 201}, response.text
                elapsed = perf_counter() - start
        finally:
            await stop_uvicorn_server(server, task)

    return {
        "ops": ops,
        "warmup_ops": warmup_ops,
        "total_execution_time_seconds": elapsed,
        "ops_per_second": ops / elapsed,
    }


def _build_delta(
    baseline: dict[str, Any], candidate: dict[str, Any]
) -> dict[str, float]:
    base_ops = float(baseline["ops_per_second"])
    cand_ops = float(candidate["ops_per_second"])
    base_total = float(baseline["total_execution_time_seconds"])
    cand_total = float(candidate["total_execution_time_seconds"])

    return {
        "ops_per_second_delta": cand_ops - base_ops,
        "ops_per_second_improvement_percent": ((cand_ops - base_ops) / base_ops) * 100,
        "total_execution_time_delta_seconds": cand_total - base_total,
        "total_execution_time_reduction_percent": (
            (base_total - cand_total) / base_total
        )
        * 100,
    }


def main() -> None:
    parser = argparse.ArgumentParser(
        description=(
            "Benchmark tigrbl request-response throughput and optionally compare "
            "against a baseline JSON payload."
        )
    )
    parser.add_argument("--ops", type=int, default=250)
    parser.add_argument("--warmup-ops", type=int, default=30)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--baseline", type=Path, default=None)
    parser.add_argument("--min-improvement-percent", type=float, default=25.0)
    args = parser.parse_args()

    candidate = asyncio.run(
        _run_request_response_benchmark(ops=args.ops, warmup_ops=args.warmup_ops)
    )
    payload: dict[str, Any] = {"candidate": candidate}

    if args.baseline is not None:
        baseline = json.loads(args.baseline.read_text(encoding="utf-8"))
        if "candidate" in baseline:
            baseline = baseline["candidate"]
        delta = _build_delta(baseline, candidate)
        payload["baseline"] = baseline
        payload["delta"] = delta

        improvement = delta["ops_per_second_improvement_percent"]
        if improvement < args.min_improvement_percent:
            raise SystemExit(
                "Benchmark improvement gate failed: "
                f"{improvement:.2f}% < {args.min_improvement_percent:.2f}%"
            )

    serialized = json.dumps(payload, indent=2)
    if args.output is not None:
        args.output.write_text(serialized, encoding="utf-8")
    print(serialized)


if __name__ == "__main__":
    main()
