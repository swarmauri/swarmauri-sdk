"""Simple evaluator base class for benchmark runners."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict


class Evaluator:
    """Abstract evaluator that runs a benchmark command inside a workspace."""

    last_result: Dict[str, Any] | None = None

    def run(self, workspace: Path, bench_cmd: str, runs: int = 1, **kw: Any) -> float:
        """Run the benchmark and return a scalar fitness score."""
        raise NotImplementedError

    def reset(self) -> None:
        """Clear stored result between runs."""
        self.last_result = None
