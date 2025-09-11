from pathlib import Path

import pytest

from peagen.plugins.evaluators.pytest_monitor import PytestMonitorEvaluator


@pytest.mark.unit
def test_monitor_evaluator(tmp_path: Path):
    tests = tmp_path / "tests"
    tests.mkdir()
    (tests / "test_ok.py").write_text(
        "def test_ok():\n    assert True\n", encoding="utf-8"
    )
    ev = PytestMonitorEvaluator()
    score = ev.run(tmp_path, "pytest -q")
    assert isinstance(score, float)
    assert ev.last_result is not None
    assert "median" in ev.last_result
