from __future__ import annotations

import asyncio
import json
import random
import tracemalloc
from pathlib import Path
from statistics import mean, pstdev
from tempfile import TemporaryDirectory
from time import perf_counter
from typing import Any, Callable

import httpx
import pytest

from tests.i9n.uvicorn_utils import run_uvicorn_in_task, stop_uvicorn_server
from tests.perf.helper_fastapi_create_app import (
    create_fastapi_app,
    fastapi_create_path,
    fetch_fastapi_names,
)
from tests.perf.helper_tigrbl_create_app import (
    create_tigrbl_app,
    fetch_tigrbl_names,
    initialize_tigrbl_app,
    tigrbl_create_path,
)

RESULTS_PATH = Path(__file__).with_name("benchmark_results_create_uvicorn.json")
TIGRBL_ONLY_RESULTS_PATH = Path(__file__).with_name(
    "benchmark_results_tigrbl_create_uvicorn.json"
)
SEQUENTIAL_RESULTS_PATH = Path(__file__).with_name(
    "benchmark_results_create_uvicorn_sequential_10_rounds.json"
)
SEQUENTIAL_STEPS_RESULTS_PATH = Path(__file__).with_name(
    "benchmark_results_create_uvicorn_sequential_10_steps.json"
)
OPS_COUNT = 25
BENCHMARK_ROUNDS = 3
SEQUENTIAL_ROUNDS = 10
THROUGHPUT_RATIO_TARGET = 1.25


def _summarize(values: list[float]) -> dict[str, float]:
    return {
        "min": min(values),
        "mean": mean(values),
        "max": max(values),
    }


async def _benchmark_app(
    *,
    scenario: str,
    create_app: Callable[[Path], Any],
    endpoint_path: str,
    fetch_names: Callable[[Path], list[str]],
    initialize: Callable[[Any], Any] | None = None,
) -> dict[str, Any]:
    with TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / f"{scenario}.sqlite3"
        expected_names = [f"{scenario}-{i}" for i in range(OPS_COUNT)]

        start = perf_counter()
        app = create_app(db_path)
        if initialize is not None:
            await initialize(app)
        base_url, server, task = await run_uvicorn_in_task(app)
        first_start_time = perf_counter() - start

        op_durations: list[float] = []
        op_memory_peak_bytes: list[int] = []

        try:
            async with httpx.AsyncClient(base_url=base_url, timeout=10.0) as client:
                execution_start = perf_counter()

                for _ in range(5):
                    ready = await client.get("/healthz")
                    if ready.status_code == 200:
                        break
                    await asyncio.sleep(0.05)

                tracemalloc.start()

                for item_name in expected_names:
                    mem_before_current, mem_before_peak = (
                        tracemalloc.get_traced_memory()
                    )
                    op_start = perf_counter()

                    response = await client.post(
                        endpoint_path, json={"name": item_name}
                    )
                    if response.status_code == 400:
                        await asyncio.sleep(0.05)
                        response = await client.post(
                            endpoint_path,
                            json={"name": item_name},
                        )

                    op_elapsed = perf_counter() - op_start
                    mem_after_current, mem_after_peak = tracemalloc.get_traced_memory()

                    assert response.status_code in {200, 201}, response.text
                    body = response.json()
                    assert body["name"] == item_name

                    op_durations.append(op_elapsed)
                    op_memory_peak_bytes.append(
                        max(0, mem_after_peak - mem_before_peak)
                    )
                    _ = mem_before_current, mem_after_current

                execution_total = perf_counter() - execution_start
                tracemalloc.stop()

            persisted_names = fetch_names(db_path)
            assert persisted_names == expected_names
        finally:
            await stop_uvicorn_server(server, task)

    per_op_s = _summarize(op_durations)
    per_op_mem = _summarize([float(v) for v in op_memory_peak_bytes])

    return {
        "scenario": scenario,
        "ops": OPS_COUNT,
        "first_start_seconds": first_start_time,
        "execution_total_seconds": execution_total,
        "ops_per_second": OPS_COUNT / execution_total,
        "time_per_op_seconds": per_op_s,
        "memory_peak_per_op_bytes": per_op_mem,
    }


async def _run_pair_benchmark() -> dict[str, Any]:
    tigrbl_result = await _benchmark_app(
        scenario="tigrbl",
        create_app=create_tigrbl_app,
        endpoint_path=tigrbl_create_path(),
        fetch_names=fetch_tigrbl_names,
        initialize=initialize_tigrbl_app,
    )
    fastapi_result = await _benchmark_app(
        scenario="fastapi",
        create_app=create_fastapi_app,
        endpoint_path=fastapi_create_path(),
        fetch_names=fetch_fastapi_names,
    )

    return {
        "results": [tigrbl_result, fastapi_result],
        "units": {
            "first_start_seconds": "seconds",
            "execution_total_seconds": "seconds",
            "ops_per_second": "operations/second",
            "time_per_op_seconds": "seconds",
            "memory_peak_per_op_bytes": "bytes",
        },
    }


def _run_pair_benchmark_sync() -> dict[str, Any]:
    return asyncio.run(_run_pair_benchmark())


async def _run_tigrbl_benchmark() -> dict[str, Any]:
    tigrbl_result = await _benchmark_app(
        scenario="tigrbl",
        create_app=create_tigrbl_app,
        endpoint_path=tigrbl_create_path(),
        fetch_names=fetch_tigrbl_names,
        initialize=initialize_tigrbl_app,
    )

    return {
        "results": [tigrbl_result],
        "units": {
            "first_start_seconds": "seconds",
            "execution_total_seconds": "seconds",
            "ops_per_second": "operations/second",
            "time_per_op_seconds": "seconds",
            "memory_peak_per_op_bytes": "bytes",
        },
    }


def _run_tigrbl_benchmark_sync() -> dict[str, Any]:
    return asyncio.run(_run_tigrbl_benchmark())


async def _run_sequential_consistency_benchmark() -> dict[str, Any]:
    scenario_runner = {
        "tigrbl": dict(
            create_app=create_tigrbl_app,
            endpoint_path=tigrbl_create_path(),
            fetch_names=fetch_tigrbl_names,
            initialize=initialize_tigrbl_app,
        ),
        "fastapi": dict(
            create_app=create_fastapi_app,
            endpoint_path=fastapi_create_path(),
            fetch_names=fetch_fastapi_names,
            initialize=None,
        ),
    }
    order_rng = random.Random(20260319)
    rounds: list[dict[str, Any]] = []
    steps: list[dict[str, Any]] = []

    for round_index in range(1, SEQUENTIAL_ROUNDS + 1):
        order = ["tigrbl", "fastapi"]
        order_rng.shuffle(order)
        round_results: list[dict[str, Any]] = []

        for scenario in order:
            result = await _benchmark_app(
                scenario=scenario,
                create_app=scenario_runner[scenario]["create_app"],
                endpoint_path=scenario_runner[scenario]["endpoint_path"],
                fetch_names=scenario_runner[scenario]["fetch_names"],
                initialize=scenario_runner[scenario]["initialize"],
            )
            round_results.append(result)

        rounds.append(
            {
                "round": round_index,
                "order": order,
                "results": round_results,
            }
        )
        indexed = {result["scenario"]: result for result in round_results}
        tigrbl_ops = indexed["tigrbl"]["ops_per_second"]
        fastapi_ops = indexed["fastapi"]["ops_per_second"]
        steps.append(
            {
                "step": round_index,
                "order": order,
                "ops_per_second": {
                    "tigrbl": tigrbl_ops,
                    "fastapi": fastapi_ops,
                },
                "delta_ops_per_second_tigrbl_minus_fastapi": tigrbl_ops - fastapi_ops,
                "throughput_ratio_tigrbl_over_fastapi": (
                    tigrbl_ops / fastapi_ops if fastapi_ops else 0.0
                ),
            }
        )

    per_scenario_ops: dict[str, list[float]] = {"tigrbl": [], "fastapi": []}
    for round_payload in rounds:
        for result in round_payload["results"]:
            per_scenario_ops[result["scenario"]].append(result["ops_per_second"])

    tigrbl_mean = mean(per_scenario_ops["tigrbl"])
    fastapi_mean = mean(per_scenario_ops["fastapi"])
    throughput_ratio = tigrbl_mean / fastapi_mean if fastapi_mean else 0.0

    return {
        "rounds": rounds,
        "steps": steps,
        "summary": {
            "round_count": SEQUENTIAL_ROUNDS,
            "step_count": SEQUENTIAL_ROUNDS,
            "throughput_ratio_target": THROUGHPUT_RATIO_TARGET,
            "ops_per_second": {
                "tigrbl": {
                    "min": min(per_scenario_ops["tigrbl"]),
                    "mean": tigrbl_mean,
                    "max": max(per_scenario_ops["tigrbl"]),
                    "stddev": pstdev(per_scenario_ops["tigrbl"]),
                },
                "fastapi": {
                    "min": min(per_scenario_ops["fastapi"]),
                    "mean": fastapi_mean,
                    "max": max(per_scenario_ops["fastapi"]),
                    "stddev": pstdev(per_scenario_ops["fastapi"]),
                },
            },
            "delta_ops_per_second_tigrbl_minus_fastapi": tigrbl_mean - fastapi_mean,
            "throughput_ratio_tigrbl_over_fastapi": throughput_ratio,
        },
    }


@pytest.mark.perf
@pytest.mark.benchmark(group="tigrbl_vs_fastapi_create")
def test_tigrbl_and_fastapi_create_benchmark_and_db_integrity(benchmark: Any) -> None:
    payload = benchmark.pedantic(
        _run_pair_benchmark_sync,
        iterations=1,
        rounds=BENCHMARK_ROUNDS,
    )

    stats = getattr(benchmark, "stats", None)
    stats_values = getattr(stats, "stats", stats)
    payload["pytest_benchmark"] = {
        "rounds": BENCHMARK_ROUNDS,
        "benchmark_total_seconds": float(getattr(stats_values, "mean", 0.0)),
        "benchmark_min_seconds": float(getattr(stats_values, "min", 0.0)),
        "benchmark_max_seconds": float(getattr(stats_values, "max", 0.0)),
    }
    RESULTS_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    assert RESULTS_PATH.exists()
    for scenario in payload["results"]:
        assert scenario["ops_per_second"] > 0

    assert len(payload["results"]) == 2


@pytest.mark.perf
@pytest.mark.benchmark(group="tigrbl_create")
def test_tigrbl_create_benchmark_and_db_integrity(benchmark: Any) -> None:
    payload = benchmark.pedantic(
        _run_tigrbl_benchmark_sync,
        iterations=1,
        rounds=BENCHMARK_ROUNDS,
    )

    stats = getattr(benchmark, "stats", None)
    stats_values = getattr(stats, "stats", stats)
    payload["pytest_benchmark"] = {
        "rounds": BENCHMARK_ROUNDS,
        "benchmark_total_seconds": float(getattr(stats_values, "mean", 0.0)),
        "benchmark_min_seconds": float(getattr(stats_values, "min", 0.0)),
        "benchmark_max_seconds": float(getattr(stats_values, "max", 0.0)),
    }
    TIGRBL_ONLY_RESULTS_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    assert TIGRBL_ONLY_RESULTS_PATH.exists()
    assert len(payload["results"]) == 1
    assert payload["results"][0]["scenario"] == "tigrbl"
    assert payload["results"][0]["ops_per_second"] > 0


@pytest.mark.perf
def test_tigrbl_vs_fastapi_sequential_10_rounds_consistency() -> None:
    payload = asyncio.run(_run_sequential_consistency_benchmark())
    SEQUENTIAL_RESULTS_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    assert SEQUENTIAL_RESULTS_PATH.exists()
    assert payload["summary"]["round_count"] == SEQUENTIAL_ROUNDS
    assert (
        payload["summary"]["throughput_ratio_tigrbl_over_fastapi"]
        >= THROUGHPUT_RATIO_TARGET
    )


@pytest.mark.perf
def test_tigrbl_vs_fastapi_sequential_10_steps_randomized_order() -> None:
    payload = asyncio.run(_run_sequential_consistency_benchmark())
    SEQUENTIAL_STEPS_RESULTS_PATH.write_text(
        json.dumps(payload, indent=2), encoding="utf-8"
    )

    assert SEQUENTIAL_STEPS_RESULTS_PATH.exists()
    assert payload["summary"]["step_count"] == SEQUENTIAL_ROUNDS
    assert len(payload["steps"]) == SEQUENTIAL_ROUNDS
    for step in payload["steps"]:
        assert step["order"] in (["tigrbl", "fastapi"], ["fastapi", "tigrbl"])
        assert step["throughput_ratio_tigrbl_over_fastapi"] > 0
    assert (
        payload["summary"]["throughput_ratio_tigrbl_over_fastapi"]
        >= THROUGHPUT_RATIO_TARGET
    )
