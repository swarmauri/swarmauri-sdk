from unittest.mock import MagicMock

import pytest

from peagen.plugins.evaluators.ruff_evaluator import RuffEvaluator
from swarmauri_core.programs.IProgram import IProgram


@pytest.fixture
def mock_program(tmp_path):
    program = MagicMock(spec=IProgram)
    program.path = tmp_path
    return program


def test_score_no_violations(mock_program):
    (mock_program.path / "good.py").write_text(
        "def foo():\n    pass\n", encoding="utf-8"
    )
    ev = RuffEvaluator()
    score, meta = ev._compute_score(mock_program)
    assert meta["n_violations"] == 0
    assert score == 0


def test_score_with_violations(mock_program):
    (mock_program.path / "bad.py").write_text("import os\n", encoding="utf-8")
    ev = RuffEvaluator()
    score, meta = ev._compute_score(mock_program)
    assert meta["n_violations"] >= 1
    assert score <= 0
