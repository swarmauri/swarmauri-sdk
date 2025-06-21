"""Measure wall-clock runtime of a command without pytest instrumentation.

The evaluator executes *bench_cmd* inside *workspace* using :func:`time.perf_counter`
to record runtime. It repeats the command ``runs`` times and returns the negated
median of the observed runtimes in milliseconds. A lower execution time therefore
produces a higher fitness score. The last run's details are stored in
:attr:`Evaluator.last_result`.
"""

from __future__ import annotations

import subprocess
import time
from pathlib import Path
from statistics import median
from typing import Any

from .base import Evaluator


class SimpleTimeEvaluator(Evaluator):
    """Wall-clock timing based fitness evaluator."""

    def run(self, workspace: Path, bench_cmd: str, runs: int = 1, **kw: Any) -> float:
        times = []
        for _ in range(max(1, runs)):
            start = time.perf_counter()
            subprocess.run(
                bench_cmd,
                shell=True,
                cwd=workspace,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            times.append((time.perf_counter() - start) * 1000)
        med = median(times)
        self.last_result = {"median_ms": med, "runs": runs}
        return -med
