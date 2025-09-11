from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any, Dict, Tuple, Literal

from swarmauri_base.evaluators.EvaluatorBase import EvaluatorBase
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_core.programs.IProgram import IProgram as Program


@ComponentBase.register_model()
class RuffEvaluator(EvaluatorBase):
    """Evaluator that scores code based on Ruff lint violations."""

    type: Literal["RuffEvaluator"] = "RuffEvaluator"
    max_violations: int = 200

    def _compute_score(
        self, program: Program, **kwargs: Any
    ) -> Tuple[float, Dict[str, Any]]:
        root = Path(getattr(program, "path", Path.cwd()))

        proc = subprocess.run(
            ["ruff", "check", "--quiet", str(root)],
            capture_output=True,
            text=True,
        )
        violations = [line for line in proc.stdout.splitlines() if line.strip()]
        n_violations = len(violations)

        if n_violations > self.max_violations:
            score = float("-inf")
        else:
            score = -float(n_violations)

        metadata = {"n_violations": n_violations, "violations": violations}
        return score, metadata
