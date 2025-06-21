import pytest
from peagen.plugins.evaluators.composite_evaluator import CompositeEvaluator
from swarmauri_base.evaluators.EvaluatorBase import EvaluatorBase
from swarmauri_standard.programs.Program import Program


class EvalA(EvaluatorBase):
    def _compute_score(self, program: Program, **kwargs):
        return 1.0, {"name": "A"}


class EvalB(EvaluatorBase):
    def _compute_score(self, program: Program, **kwargs):
        return 3.0, {"name": "B"}


@pytest.mark.unit
def test_composite_weighting():
    program = Program()
    evaluator = CompositeEvaluator([EvalA, EvalB], weights=[0.25, 0.75])
    score, meta = evaluator.evaluate(program)
    expected = (1.0 * 0.25 + 3.0 * 0.75) / (0.25 + 0.75)
    assert score == pytest.approx(expected)
    assert meta["scores"] == [1.0, 3.0]
    assert meta["weights"] == [0.25, 0.75]
