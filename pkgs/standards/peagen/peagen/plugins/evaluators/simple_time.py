"""Measure wall-clock runtime of a command using :func:`time.perf_counter`.\n\nThe evaluator runs ``bench_cmd`` inside ``workspace`` ``runs`` times and\nrecords each duration in milliseconds. The median runtime is negated and\nreturned as the fitness score so that faster executions yield higher\nfitness. Details of each run are stored in :attr:`last_result`.\n"""

from __future__ import annotations

import statistics
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List


@dataclass
class Evaluator:
    """Base class for Peagen fitness evaluators."""

    last_result: Dict[str, Any] = field(default_factory=dict, init=False)

    def run(self, workspace: Path, bench_cmd: str, runs: int = 1, **kw: Any) -> float:
        raise NotImplementedError


class SimpleTimeEvaluator(Evaluator):
    """Median wall-clock time of a command (lower is better)."""

    def run(self, workspace: Path, bench_cmd: str, runs: int = 1, **kw: Any) -> float:
        durations: List[float] = []
        for _ in range(max(1, runs)):
            start = time.perf_counter()
            subprocess.run(
                bench_cmd,
                shell=True,
                cwd=workspace,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            durations.append((time.perf_counter() - start) * 1000)

        median_ms = statistics.median(durations)
        self.last_result = {
            "runs": len(durations),
            "times_ms": [round(t, 3) for t in durations],
            "median_ms": round(median_ms, 3),
        }
        return -median_ms
