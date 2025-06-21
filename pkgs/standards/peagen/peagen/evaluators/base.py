"""Core classes for Peagen fitness evaluators."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict


class Evaluator:
    """Minimal evaluator interface storing the last result."""

    last_result: Dict[str, Any] | None

    def __init__(self) -> None:
        self.last_result = None

    def run(self, workspace: Path, bench_cmd: str, runs: int = 1, **kw: Any) -> float:
        """Execute the evaluation and return a fitness score."""
        raise NotImplementedError
