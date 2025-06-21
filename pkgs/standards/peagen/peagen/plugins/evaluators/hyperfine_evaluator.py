from __future__ import annotations

import json
import shlex
import shutil
import subprocess
import tempfile
from pathlib import Path
from typing import Any, Dict, Tuple, Literal

from swarmauri_base.evaluators.EvaluatorBase import EvaluatorBase
from swarmauri_core.ComponentBase import ComponentBase
from swarmauri_core.programs.IProgram import IProgram as Program


@ComponentBase.register_model()
class HyperfineEvaluator(EvaluatorBase):
    """Evaluator that measures command performance via `hyperfine`."""

    type: Literal["HyperfineEvaluator"] = "HyperfineEvaluator"

    bench_cmd: str
    runs: int = 6
    warmup: int = 1

    # ------------------------------------------------------------------
    @staticmethod
    def _to_ms(value: float, unit: str) -> float:
        if unit.startswith("nano"):
            return value / 1_000_000
        if unit.startswith("micro"):
            return value / 1_000
        if unit.startswith("milli"):
            return value
        return value * 1_000

    # ------------------------------------------------------------------
    def _compute_score(
        self, program: Program, **kwargs: Any
    ) -> Tuple[float, Dict[str, Any]]:
        tmp_dir = tempfile.mkdtemp()
        try:
            for rel, text in program.get_source_files().items():
                dst = Path(tmp_dir) / rel
                dst.parent.mkdir(parents=True, exist_ok=True)
                dst.write_text(text, encoding="utf-8")

            json_path = Path(tmp_dir) / "hyperfine.json"
            cmd = (
                f"hyperfine -i -m {self.runs} --warmup {self.warmup} --export-json {json_path} "
                f"{self.bench_cmd}"
            )
            proc = subprocess.run(
                shlex.split(cmd), cwd=tmp_dir, capture_output=True, text=True
            )
            if proc.returncode != 0:
                raise RuntimeError(proc.stderr.strip())

            data = json.loads(json_path.read_text())
            unit = data.get("time_unit", "second")
            results = data.get("results", [])
            median = results[0].get("median") if results else None
            if median is None:
                raise RuntimeError("No hyperfine results")
            ms = self._to_ms(median, unit)
            score = -ms
            return score, {"median_ms": ms}
        finally:
            shutil.rmtree(tmp_dir, ignore_errors=True)
