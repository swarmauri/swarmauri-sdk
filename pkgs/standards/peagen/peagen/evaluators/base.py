"""Base classes for Peagen fitness evaluators."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict


class Evaluator:
    """Simple evaluator interface."""

    last_result: Dict[str, Any] | None

    def __init__(self, **_: Any) -> None:
        self.last_result = None

    def run(self, workspace: Path, bench_cmd: str, runs: int = 1, **kw: Any) -> float:
        """Execute *bench_cmd* in *workspace* ``runs`` times and return a fitness."""
        raise NotImplementedError
