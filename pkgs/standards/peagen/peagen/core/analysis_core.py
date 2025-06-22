from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List
import statistics


def aggregate_evaluations(run_dirs: List[Path]) -> List[Dict[str, Any]]:
    """Return evaluation summaries for each run directory."""
    summaries: List[Dict[str, Any]] = []
    for rd in run_dirs:
        report_path = rd / ".peagen" / "eval_results.json"
        if not report_path.exists():
            continue
        data = json.loads(report_path.read_text())
        scores = [r.get("score", 0.0) for r in data.get("results", [])]
        avg_score = statistics.mean(scores) if scores else float("inf")
        summaries.append(
            {
                "run_dir": str(rd),
                "avg_score": avg_score,
                "detail": data,
            }
        )
    return summaries


def analyze_runs(run_dirs: List[Path], *, spec_name: str) -> Dict[str, Any]:
    """Aggregate evaluation results and pick the best run."""
    summaries = aggregate_evaluations(run_dirs)
    summaries.sort(key=lambda s: s["avg_score"])
    winner = summaries[0]["run_dir"] if summaries else None
    result = {"runs": summaries, "winner": winner}
    if run_dirs:
        out_file = run_dirs[0].parent / f"{spec_name}_analysis.json"
        out_file.write_text(json.dumps(result, indent=2))
        result["results_file"] = str(out_file)
    return result
