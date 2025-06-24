"""benchmark.py

Measure median wall-clock time per pytest test using pytest-benchmark.

The evaluator runs ``pytest`` with the benchmark plugin enabled and reads
``benchmark.json`` to obtain the median runtime for each test. The median
across all tests and runs is negated so that lower values correspond to
higher fitness.
"""

from __future__ import annotations

import json
import shlex
import statistics
import subprocess
from pathlib import Path
from typing import Any, List

from .base import Evaluator


class PytestBenchmarkEvaluator(Evaluator):
    """Run pytest-benchmark and score by median time."""

    def run(self, workspace: Path, bench_cmd: str, runs: int = 1, **kw: Any) -> float:
        workspace = Path(workspace)
        times: List[float] = []
        bench_args = [
            "pytest",
            "--benchmark-only",
            "--benchmark-json=benchmark.json",
            "--json-report",
            "-q",
        ]
        bench_args.extend(shlex.split(bench_cmd))

        for _ in range(max(1, runs)):
            subprocess.run(bench_args, cwd=workspace, capture_output=True, text=True)
            bench_file = workspace / "benchmark.json"
            if bench_file.exists():
                data = json.loads(bench_file.read_text())
                for entry in data.get("benchmarks", []):
                    median_s = entry.get("stats", {}).get("median")
                    if isinstance(median_s, (int, float)):
                        times.append(median_s * 1000)
                bench_file.unlink()
            report_file = workspace / ".report.json"
            report_file.unlink(missing_ok=True)

        if not times:
            self.last_result = {"median_ms": None}
            return float("-inf")

        median_ms = statistics.median(times)
        self.last_result = {"median_ms": median_ms, "runs": len(times)}
        return -median_ms
