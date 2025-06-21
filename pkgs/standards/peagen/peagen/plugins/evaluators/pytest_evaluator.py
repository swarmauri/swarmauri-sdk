"""Pytest-based fitness evaluator."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any, Dict, Literal, Tuple

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.evaluators.EvaluatorBase import EvaluatorBase
from swarmauri_core.programs.IProgram import IProgram as Program


@ComponentBase.register_model()
class PytestEvaluator(EvaluatorBase):
    """Run pytest in a workspace and score by pass ratio."""

    type: Literal["PytestEvaluator"] = "PytestEvaluator"
    test_timeout: float = 60.0
    partial: Literal["all", "touched"] = "all"

    def _compute_score(
        self, program: Program, **kwargs: Any
    ) -> Tuple[float, Dict[str, Any]]:
        """Execute pytest and return the pass ratio as fitness."""
        workspace = Path(kwargs.get("workspace", Path.cwd()))

        cmd = ["pytest", "--json-report", "--maxfail=1", "-q"]
        if self.partial == "touched":
            cmd.append("--last-failed")

        proc = subprocess.run(
            cmd,
            cwd=workspace,
            capture_output=True,
            text=True,
            timeout=self.test_timeout,
        )

        report_file = workspace / ".report.json"
        if not report_file.exists():
            return 0.0, {"stdout": proc.stdout, "stderr": proc.stderr}

        data = json.loads(report_file.read_text())
        summary = data.get("summary", {})
        passed = summary.get("passed", 0)
        failed = summary.get("failed", 0)
        errors = summary.get("errors", 0)
        total = passed + failed + errors
        ratio = passed / total if total else 0.0
        metadata = {"passed": passed, "failed": failed, "errors": errors}
        report_file.unlink(missing_ok=True)
        return ratio, metadata
