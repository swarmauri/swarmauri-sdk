"""Capture resource usage from pytest runs via the pytest-monitor plugin.

The evaluator launches pytest with ``pytest-monitor`` enabled and reads the
``.pymon.sqlite`` database produced for each run. It reports either the peak
resident set size (RSS) or mean CPU utilisation across all collected tests.
Smaller resource consumption yields higher fitness by default.
"""

from __future__ import annotations

import shlex
import sqlite3
import statistics
import subprocess
from pathlib import Path
from typing import Any

from .base import Evaluator


class PytestMonitorEvaluator(Evaluator):
    """Evaluate resource usage using pytest-monitor."""

    def __init__(self, metric: str = "rss", inverse: bool = True) -> None:
        self.metric = metric
        self.inverse = inverse

    def _collect_metric(self, db_path: Path) -> float:
        with sqlite3.connect(db_path) as conn:
            rows = conn.execute(
                "SELECT MEM_USAGE, CPU_USAGE FROM TEST_METRICS"
            ).fetchall()
        rss_vals = [r[0] for r in rows]
        cpu_vals = [r[1] for r in rows]
        peak_rss = max(rss_vals) if rss_vals else 0.0
        mean_cpu = sum(cpu_vals) / len(cpu_vals) if cpu_vals else 0.0
        return peak_rss if self.metric == "rss" else mean_cpu

    def run(self, workspace: Path, bench_cmd: str, runs: int = 1, **kw: Any) -> float:
        values = []
        for _ in range(runs):
            cmd = shlex.split(bench_cmd) + ["--json-report", "--db", ".pymon.sqlite"]
            subprocess.run(cmd, cwd=workspace, check=False, capture_output=True)
            metric = self._collect_metric(workspace / ".pymon.sqlite")
            (workspace / ".pymon.sqlite").unlink(missing_ok=True)
            values.append(metric)
        median_v = statistics.median(values)
        score = -median_v if self.inverse else median_v
        self.last_result = {
            "metric": self.metric,
            "runs": runs,
            "values": values,
            "median": median_v,
        }
        return score
