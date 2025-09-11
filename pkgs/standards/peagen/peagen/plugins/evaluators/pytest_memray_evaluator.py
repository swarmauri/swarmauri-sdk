"""Measure peak heap allocation per test via pytest-memray.

This evaluator runs pytest with the ``pytest-memray`` plugin enabled. Memory
allocation metadata is collected for each test and the largest ``peak_memory``
value across all tests is used to compute the fitness score. Smaller memory
usage results in a higher score.
"""

from __future__ import annotations

import json
import pickle
import shutil
import subprocess
from pathlib import Path
from typing import Any, Dict, Tuple, Literal

from swarmauri_base.evaluators.EvaluatorBase import EvaluatorBase
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_core.programs.IProgram import IProgram as Program


@ComponentBase.register_model()
class PytestMemrayEvaluator(EvaluatorBase):
    """Return fitness based on peak heap usage recorded by pytest-memray."""

    type: Literal["PytestMemrayEvaluator"] = "PytestMemrayEvaluator"

    def _compute_score(
        self, program: Program, **kwargs: Any
    ) -> Tuple[float, Dict[str, Any]]:
        workspace = Path(getattr(program, "path", Path.cwd()))
        bin_dir = workspace / ".memray_bins"
        if bin_dir.exists():
            shutil.rmtree(bin_dir, ignore_errors=True)
        cmd = [
            "pytest",
            "--memray",
            f"--memray-bin-path={bin_dir}",
            "--json-report",
            "-q",
        ]
        subprocess.run(cmd, cwd=workspace, check=False)

        peak_bytes = 0
        meta_dir = bin_dir / "metadata"
        if meta_dir.exists():
            for meta_file in meta_dir.glob("*.metadata"):
                with open(meta_file, "rb") as fh:
                    result = pickle.load(fh)
                    peak_bytes = max(peak_bytes, result.metadata.peak_memory)

        report_file = workspace / ".report.json"
        summary = {}
        if report_file.exists():
            data = json.loads(report_file.read_text())
            summary = data.get("summary", {})
            report_file.unlink()

        peak_mib = peak_bytes / (1024 * 1024)
        details = {
            "peak_mib": peak_mib,
            "passed": summary.get("passed", 0),
            "failed": summary.get("failed", 0),
        }
        return -peak_mib, details
