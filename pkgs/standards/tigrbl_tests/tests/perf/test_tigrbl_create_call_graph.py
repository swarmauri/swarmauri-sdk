from __future__ import annotations

import asyncio
import cProfile
import json
import pstats
from pathlib import Path
from tempfile import TemporaryDirectory
from time import perf_counter
from typing import Any

import httpx
import pytest

from tests.i9n.uvicorn_utils import run_uvicorn_in_task, stop_uvicorn_server
from tests.perf.helper_tigrbl_create_app import (
    create_tigrbl_app,
    fetch_tigrbl_names,
    initialize_tigrbl_app,
    tigrbl_create_path,
)

OPS_COUNT = 250
TOP_FUNCTION_LIMIT = 75
TOP_EDGE_LIMIT = 150
RESULTS_PATH = Path(__file__).with_name("tigrbl_create_call_graph_250_ops.json")


def _func_label(func_key: tuple[str, int, str]) -> str:
    file_name, line_no, func_name = func_key
    return f"{func_name} ({file_name}:{line_no})"


def _build_top_functions(stats: pstats.Stats, *, limit: int) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for func_key, values in stats.stats.items():
        primitive_calls, total_calls, total_time, cumulative_time, _ = values
        rows.append(
            {
                "function": _func_label(func_key),
                "primitive_calls": int(primitive_calls),
                "total_calls": int(total_calls),
                "total_time_seconds": float(total_time),
                "cumulative_time_seconds": float(cumulative_time),
            }
        )

    rows.sort(key=lambda row: row["cumulative_time_seconds"], reverse=True)
    return rows[:limit]


def _build_call_edges(stats: pstats.Stats, *, limit: int) -> list[dict[str, Any]]:
    edges: list[dict[str, Any]] = []

    for callee_key, values in stats.stats.items():
        callers = values[4]
        callee_label = _func_label(callee_key)

        for caller_key, caller_metrics in callers.items():
            caller_label = _func_label(caller_key)
            call_count = int(caller_metrics[0])
            total_time_seconds = float(caller_metrics[2])
            cumulative_time_seconds = float(caller_metrics[3])
            edges.append(
                {
                    "caller": caller_label,
                    "callee": callee_label,
                    "call_count": call_count,
                    "total_time_seconds": total_time_seconds,
                    "cumulative_time_seconds": cumulative_time_seconds,
                }
            )

    edges.sort(
        key=lambda edge: (
            edge["cumulative_time_seconds"],
            edge["total_time_seconds"],
            edge["call_count"],
        ),
        reverse=True,
    )
    return edges[:limit]


async def _profile_create_call_graph(*, results_path: Path) -> dict[str, Any]:
    with TemporaryDirectory() as tmp_dir:
        base_dir = Path(tmp_dir)
        db_path = base_dir / "tigrbl-create-call-graph.sqlite3"

        app = create_tigrbl_app(db_path)
        await initialize_tigrbl_app(app)

        expected_names = [f"profiled-create-{idx}" for idx in range(OPS_COUNT)]

        base_url, server, task = await run_uvicorn_in_task(app)
        profiler = cProfile.Profile()
        start = perf_counter()

        try:
            async with httpx.AsyncClient(base_url=base_url, timeout=20.0) as client:
                health = await client.get("/healthz")
                assert health.status_code == 200

                profiler.enable()
                for item_name in expected_names:
                    response = await client.post(
                        tigrbl_create_path(),
                        json={"name": item_name},
                    )
                    assert response.status_code in {200, 201}, response.text
                    assert response.json()["name"] == item_name
                profiler.disable()
        finally:
            await stop_uvicorn_server(server, task)

        persisted_names = fetch_tigrbl_names(db_path)
        assert persisted_names == expected_names

        elapsed = perf_counter() - start

        stats = pstats.Stats(profiler).strip_dirs()
        top_functions = _build_top_functions(stats, limit=TOP_FUNCTION_LIMIT)
        call_edges = _build_call_edges(stats, limit=TOP_EDGE_LIMIT)

        payload = {
            "ops": OPS_COUNT,
            "endpoint": tigrbl_create_path(),
            "elapsed_seconds": elapsed,
            "call_graph": {
                "top_functions": top_functions,
                "edges": call_edges,
                "node_count": len(
                    {edge["caller"] for edge in call_edges}
                    | {edge["callee"] for edge in call_edges}
                ),
                "edge_count": len(call_edges),
            },
            "artifact_path": str(results_path),
        }

        results_path.parent.mkdir(parents=True, exist_ok=True)
        results_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        assert results_path.exists()

        return payload


@pytest.mark.perf
def test_tigrbl_create_call_graph_250_ops() -> None:
    """Profile the full client->server create flow and export a call graph artifact."""
    payload = asyncio.run(_profile_create_call_graph(results_path=RESULTS_PATH))

    assert payload["ops"] == OPS_COUNT
    assert payload["call_graph"]["edge_count"] > 0
    assert payload["call_graph"]["node_count"] > 0
    assert payload["call_graph"]["top_functions"]
    assert payload["artifact_path"] == str(RESULTS_PATH)
