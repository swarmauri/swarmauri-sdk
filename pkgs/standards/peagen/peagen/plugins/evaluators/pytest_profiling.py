"""Measure CPU time using :mod:`pytest-profiling` and :mod:`pytest-json-report`.

This evaluator profiles each test run with ``pytest --profile`` and parses the
generated ``prof/combined.prof`` file. The cumulative CPU seconds (``tottime``)
across all functions represent the test suite's CPU cost. The returned fitness
is the negative median CPU time from all runs. ``last_result`` contains a small
JSON-serialisable summary with per-run details.
"""

from __future__ import annotations

import json
import shlex
import subprocess
from pathlib import Path
from statistics import median
from typing import Any, Dict, List
import pstats

from .base import Evaluator


class PytestProfilingEvaluator(Evaluator):
    """Fitness based on CPU time recorded by pytest-profiling."""

    def run(self, workspace: Path, bench_cmd: str, runs: int = 1, **kw: Any) -> float:
        cmd_base = shlex.split(bench_cmd)
        scores: List[float] = []
        details: List[Dict[str, Any]] = []

        for _ in range(max(1, runs)):
            cmd = cmd_base + ["--profile", "--json-report", "-q"]
            subprocess.run(cmd, cwd=workspace, capture_output=True, text=True)

            prof_path = workspace / "prof" / "combined.prof"
            if not prof_path.exists():
                continue
            stats = pstats.Stats(str(prof_path))
            cpu_s = stats.total_tt
            scores.append(cpu_s)

            report_file = workspace / ".report.json"
            if report_file.exists():
                report_data = json.loads(report_file.read_text())
                summary = report_data.get("summary", {})
                details.append({"cpu_s": cpu_s, **summary})
                report_file.unlink()
            else:
                details.append({"cpu_s": cpu_s})

            prof_path.unlink()
            prof_path.parent.rmdir()

        if not scores:
            self.last_result = {"error": "profiling_failed"}
            return 0.0

        median_cpu = median(scores)
        self.last_result = {
            "runs": len(scores),
            "median_cpu_s": median_cpu,
            "runs_detail": details,
        }
        return -median_cpu
