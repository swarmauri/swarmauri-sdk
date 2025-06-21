import pytest
from peagen.plugins.evaluators.pytest_evaluator import PytestEvaluator
from swarmauri_standard.programs.Program import Program


@pytest.mark.unit
def test_pytest_evaluator_pass(tmp_path):
    tests_dir = tmp_path / "tests"
    tests_dir.mkdir()
    (tests_dir / "test_ok.py").write_text("def test_ok():\n    assert True\n")
    program = Program.from_workspace(tmp_path)
    evaluator = PytestEvaluator(test_timeout=10.0)
    score, meta = evaluator.evaluate(program, workspace=tmp_path)
    assert score == 1.0
    assert meta["passed"] == 1
