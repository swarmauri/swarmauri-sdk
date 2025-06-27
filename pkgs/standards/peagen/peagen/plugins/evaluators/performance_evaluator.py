from __future__ import annotations

import importlib
import inspect
import random
import shutil
import sys
import tempfile
import time
from pathlib import Path
from typing import Any, Dict, Tuple, Literal

import tracemalloc
from swarmauri_base.evaluators.EvaluatorBase import EvaluatorBase
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_core.programs.IProgram import IProgram as Program


@ComponentBase.register_model()
class PerformanceEvaluator(EvaluatorBase):
    """Simple evaluator measuring runtime and memory usage of a callable."""

    type: Literal["PerformanceEvaluator"] = "PerformanceEvaluator"

    def __init__(
        self,
        import_path: str,
        entry_fn: str,
        profile_mod: str | None = None,
        **data: Any,
    ) -> None:
        super().__init__(**data)
        self.import_path = import_path
        self.entry_fn = entry_fn
        self.profile_mod = profile_mod

    # ------------------------------------------------------------------
    def _profile(self, fn) -> Tuple[float, float]:
        req_pos = [
            p
            for p in inspect.signature(fn).parameters.values()
            if p.kind in (p.POSITIONAL_ONLY, p.POSITIONAL_OR_KEYWORD)
            and p.default is p.empty
        ]
        if len(req_pos) >= 2:
            rng = random.Random(42)
            graph = {i: [(rng.randrange(20), rng.randint(1, 10))] for i in range(20)}
            args = (graph, 0)
        elif len(req_pos) == 1:
            args = (random.randint(0, 100),)
        else:
            args = ()

        tracemalloc.start()
        t0 = time.perf_counter()
        try:
            fn(*args)
        except Exception:
            tracemalloc.stop()
            # Use infinity to ensure failed executions never win
            return float("inf"), float("inf")
        ms = (time.perf_counter() - t0) * 1_000
        peak = tracemalloc.get_traced_memory()[1] / 1024
        tracemalloc.stop()
        return ms, peak

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

            sys.path.insert(0, tmp_dir)
            importlib.invalidate_caches()
            mod = importlib.import_module(self.import_path)
            fn = getattr(mod, self.entry_fn)
            ms, peak = self._profile(fn)
            score = ms
            return score, {"ms": ms, "peak_kb": peak}
        finally:
            sys.path.pop(0)
            shutil.rmtree(tmp_dir, ignore_errors=True)
