from pathlib import Path

from peagen.plugins.evaluators.simple_time import SimpleTimeEvaluator


def test_simple_time_runs_command(tmp_path: Path) -> None:
    script = tmp_path / "sleep.py"
    script.write_text("import time; time.sleep(0.01)", encoding="utf-8")

    ev = SimpleTimeEvaluator()
    score = ev.run(tmp_path, f"python {script.name}", runs=2)

    assert "median_ms" in ev.last_result
    assert ev.last_result["runs"] == 2
    # runtime should be >=10ms
    assert ev.last_result["median_ms"] >= 10
    # score is negative median
    assert abs(score + ev.last_result["median_ms"]) < 1e-3
