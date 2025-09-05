import pytest
from peagen.plugins.evaluators.pytest_memray_evaluator import PytestMemrayEvaluator
from swarmauri_standard.programs.Program import Program


@pytest.mark.unit
def test_pytest_memray_evaluator(tmp_path):
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_ok.py").write_text(
        "def test_ok():\n    x=[0]*10\n    assert x\n"
    )
    program = Program.from_workspace(tmp_path)
    evaluator = PytestMemrayEvaluator()
    score, meta = evaluator.evaluate(program, workspace=tmp_path)
    assert "peak_mib" in meta
    assert score <= 0
