import json
from pathlib import Path
from unittest.mock import patch

from peagen.plugins.evaluators.pytest_perf_regression import (
    PytestPerfRegressionEvaluator,
)


def test_perf_regression_reads_speedup(tmp_path: Path):
    report = {"perf": {"speedup": 1.5}}
    (tmp_path / ".report.json").write_text(json.dumps(report), encoding="utf-8")

    with patch("subprocess.run") as run:
        ev = PytestPerfRegressionEvaluator(baseline="deadbeef")
        score = ev.run(tmp_path, "tests")
        run.assert_called()

    assert score == 1.5
    assert ev.last_result == {"baseline": "deadbeef", "speedup": 1.5}
