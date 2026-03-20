from __future__ import annotations

import asyncio
import json
import logging
import random
from pathlib import Path
from statistics import mean, median, pstdev
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
SEQUENTIAL_RESULTS_PATH = Path(__file__).with_name(
    "benchmark_results_create_uvicorn_sequential_10_rounds.json"
)
OPS_COUNT = 25
SEQUENTIAL_ROUNDS = 10
THROUGHPUT_RATIO_TARGET = 2.0


def _summarize(values: list[float]) -> dict[str, float]:
    return {
        "min": min(values),
        "mean": mean(values),
        "max": max(values),
    }


def _quantile(values: list[float], q: float) -> float:
    ordered = sorted(values)
    if not ordered:
        return 0.0
    if len(ordered) == 1:
        return ordered[0]
    pos = (len(ordered) - 1) * q
    lo = int(pos)
    hi = min(lo + 1, len(ordered) - 1)
    frac = pos - lo
    return ordered[lo] * (1.0 - frac) + ordered[hi] * frac


def _ops_summary(values: list[float]) -> dict[str, float | int]:
    q1 = _quantile(values, 0.25)
    q3 = _quantile(values, 0.75)
    iqr = q3 - q1
    low = q1 - 1.5 * iqr
    high = q3 + 1.5 * iqr
    outliers = sum(1 for value in values if value < low or value > high)
    return {
        "min": min(values),
        "max": max(values),
        "mean": mean(values),
        "stddev": pstdev(values),
        "median": median(values),
        "iqr": iqr,
        "outliers": outliers,
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
        try:
            async with httpx.AsyncClient(base_url=base_url, timeout=10.0) as client:
                for _ in range(5):
                    ready = await client.get("/healthz")
                    if ready.status_code == 200:
                        break
                    await asyncio.sleep(0.05)

                execution_start = perf_counter()

                for item_name in expected_names:
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
                    assert response.status_code in {200, 201}, response.text
                    body = response.json()
                    assert body["name"] == item_name

                    op_durations.append(op_elapsed)

                execution_total = perf_counter() - execution_start

            persisted_names = fetch_names(db_path)
            assert persisted_names == expected_names
        finally:
            await stop_uvicorn_server(server, task)

    per_op_s = _summarize(op_durations)

    return {
        "scenario": scenario,
        "ops": OPS_COUNT,
        "first_start_seconds": first_start_time,
        "execution_total_seconds": execution_total,
        "ops_per_second": OPS_COUNT / execution_total,
        "time_per_op_seconds": per_op_s,
    }


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
    delta_ops_values = [
        step["delta_ops_per_second_tigrbl_minus_fastapi"] for step in steps
    ]

    return {
        "rounds": rounds,
        "steps": steps,
        "summary": {
            "round_count": SEQUENTIAL_ROUNDS,
            "step_count": SEQUENTIAL_ROUNDS,
            "throughput_ratio_target": THROUGHPUT_RATIO_TARGET,
            "ops_per_second": {
                "tigrbl": _ops_summary(per_scenario_ops["tigrbl"]),
                "fastapi": _ops_summary(per_scenario_ops["fastapi"]),
            },
            "delta_ops_per_second_tigrbl_minus_fastapi": tigrbl_mean - fastapi_mean,
            "delta_ops_per_second_tigrbl_minus_fastapi_summary": _ops_summary(
                delta_ops_values
            ),
            "throughput_ratio_tigrbl_over_fastapi": throughput_ratio,
        },
    }


@pytest.mark.perf
def test_tigrbl_vs_fastapi_sequential_10_rounds_randomized_comparison() -> None:
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    payload = asyncio.run(_run_sequential_consistency_benchmark())
    RESULTS_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    SEQUENTIAL_RESULTS_PATH.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    summary = payload["summary"]
    print("\n[perf] per-round randomized sequential order")
    for step in payload["steps"]:
        print(
            "[perf] round={round} order={order} tigrbl_ops/s={tigrbl:.3f} "
            "fastapi_ops/s={fastapi:.3f} delta={delta:.3f} ratio={ratio:.3f}".format(
                round=step["step"],
                order="->".join(step["order"]),
                tigrbl=step["ops_per_second"]["tigrbl"],
                fastapi=step["ops_per_second"]["fastapi"],
                delta=step["delta_ops_per_second_tigrbl_minus_fastapi"],
                ratio=step["throughput_ratio_tigrbl_over_fastapi"],
            )
        )

    print(
        (
            "\n[perf] tigrbl ops/s min={t_min:.3f} max={t_max:.3f} "
            "mean={t_mean:.3f} stddev={t_std:.3f} median={t_median:.3f} "
            "iqr={t_iqr:.3f} outliers={t_out}\n"
            "[perf] fastapi ops/s min={f_min:.3f} max={f_max:.3f} "
            "mean={f_mean:.3f} stddev={f_std:.3f} median={f_median:.3f} "
            "iqr={f_iqr:.3f} outliers={f_out}\n"
            "[perf] delta_ops/s={delta:.3f} ratio_tigrbl_over_fastapi={ratio:.3f}"
        ).format(
            t_min=summary["ops_per_second"]["tigrbl"]["min"],
            t_max=summary["ops_per_second"]["tigrbl"]["max"],
            t_mean=summary["ops_per_second"]["tigrbl"]["mean"],
            t_std=summary["ops_per_second"]["tigrbl"]["stddev"],
            t_median=summary["ops_per_second"]["tigrbl"]["median"],
            t_iqr=summary["ops_per_second"]["tigrbl"]["iqr"],
            t_out=summary["ops_per_second"]["tigrbl"]["outliers"],
            f_min=summary["ops_per_second"]["fastapi"]["min"],
            f_max=summary["ops_per_second"]["fastapi"]["max"],
            f_mean=summary["ops_per_second"]["fastapi"]["mean"],
            f_std=summary["ops_per_second"]["fastapi"]["stddev"],
            f_median=summary["ops_per_second"]["fastapi"]["median"],
            f_iqr=summary["ops_per_second"]["fastapi"]["iqr"],
            f_out=summary["ops_per_second"]["fastapi"]["outliers"],
            delta=summary["delta_ops_per_second_tigrbl_minus_fastapi"],
            ratio=summary["throughput_ratio_tigrbl_over_fastapi"],
        )
    )
    print(
        (
            "[perf] delta ops/s min={d_min:.3f} max={d_max:.3f} "
            "mean={d_mean:.3f} stddev={d_std:.3f} median={d_median:.3f} "
            "iqr={d_iqr:.3f} outliers={d_out}"
        ).format(
            d_min=summary["delta_ops_per_second_tigrbl_minus_fastapi_summary"]["min"],
            d_max=summary["delta_ops_per_second_tigrbl_minus_fastapi_summary"]["max"],
            d_mean=summary["delta_ops_per_second_tigrbl_minus_fastapi_summary"]["mean"],
            d_std=summary["delta_ops_per_second_tigrbl_minus_fastapi_summary"][
                "stddev"
            ],
            d_median=summary["delta_ops_per_second_tigrbl_minus_fastapi_summary"][
                "median"
            ],
            d_iqr=summary["delta_ops_per_second_tigrbl_minus_fastapi_summary"]["iqr"],
            d_out=summary["delta_ops_per_second_tigrbl_minus_fastapi_summary"][
                "outliers"
            ],
        )
    )

    assert RESULTS_PATH.exists()
    assert SEQUENTIAL_RESULTS_PATH.exists()
    assert summary["round_count"] == SEQUENTIAL_ROUNDS
    assert summary["step_count"] == SEQUENTIAL_ROUNDS
    assert len(payload["steps"]) == SEQUENTIAL_ROUNDS
    for step in payload["steps"]:
        assert step["order"] in (["tigrbl", "fastapi"], ["fastapi", "tigrbl"])
        assert step["throughput_ratio_tigrbl_over_fastapi"] > 0
    assert summary["throughput_ratio_tigrbl_over_fastapi"] >= THROUGHPUT_RATIO_TARGET
