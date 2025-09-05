"""psutil-based disk I/O evaluator.

Measure total bytes read and written while running a benchmark command.
The fitness score is the negative median MiB delta across runs so lower
I/O usage yields a higher fitness value.
"""

from __future__ import annotations

import shlex
import statistics
import subprocess
import time
from pathlib import Path
from typing import Any

import psutil

from .base import Evaluator


class PsutilIOEvaluator(Evaluator):
    """Evaluate disk I/O usage of ``bench_cmd`` using psutil."""

    def run(self, workspace: Path, bench_cmd: str, runs: int = 1, **kw: Any) -> float:
        deltas: list[float] = []
        runs = max(1, int(runs))
        for _ in range(runs):
            before = psutil.disk_io_counters()
            start = time.perf_counter()
            subprocess.run(
                shlex.split(bench_cmd), cwd=workspace, check=False, capture_output=True
            )
            duration = time.perf_counter() - start
            after = psutil.disk_io_counters()
            delta = (after.read_bytes - before.read_bytes) + (
                after.write_bytes - before.write_bytes
            )
            deltas.append(delta / (1024 * 1024))
        median_delta = statistics.median(deltas)
        self.last_result = {
            "deltas_mib": deltas,
            "median_mib": median_delta,
            "runs": runs,
            "duration_s": duration,
        }
        return -median_delta
