"""Common evaluator base classes."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, Optional


class Evaluator:
    """Abstract evaluator interface."""

    last_result: Optional[Dict[str, Any]] = None

    def run(self, workspace: Path, bench_cmd: str, runs: int = 1, **kw: Any) -> float:
        """Execute the evaluator.

        Args:
            workspace: Path to the workspace containing tests or bench script.
            bench_cmd: Command to run for benchmarking.
            runs: Number of times to execute the benchmark.
            **kw: Extra options for derived evaluators.

        Returns:
            A scalar fitness score where higher is better.
        """
        raise NotImplementedError
