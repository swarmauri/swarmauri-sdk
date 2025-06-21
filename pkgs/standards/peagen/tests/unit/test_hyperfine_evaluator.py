import json
from types import SimpleNamespace
from pathlib import Path

import pytest

from peagen.plugins.evaluators.hyperfine_evaluator import HyperfineEvaluator
from swarmauri_standard.programs.Program import Program


@pytest.mark.unit
def test_hyperfine_evaluator_runs(monkeypatch, tmp_path: Path):
    workspace = tmp_path / "ws"
    workspace.mkdir()
    (workspace / "app.py").write_text("print('hi')", encoding="utf-8")
    program = Program.from_workspace(workspace)

    def fake_run(cmd, cwd=None, capture_output=True, text=True):
        (Path(cwd) / "hyperfine.json").write_text(
            json.dumps(
                {
                    "time_unit": "second",
                    "results": [{"median": 0.05}],
                }
            ),
            encoding="utf-8",
        )
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    import peagen.plugins.evaluators.hyperfine_evaluator as hf_mod

    monkeypatch.setattr(hf_mod.subprocess, "run", fake_run)

    evaluator = HyperfineEvaluator(bench_cmd="python app.py")
    score, meta = evaluator.evaluate(program)
    assert score == pytest.approx(-50.0)
    assert meta["median_ms"] == pytest.approx(50.0)
