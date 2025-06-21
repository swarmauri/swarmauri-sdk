"""Built-in fitness evaluators used by ``peagen eval``."""

from .base import Evaluator
from .pytest_perf_regression import PytestPerfRegressionEvaluator

__all__ = ["Evaluator", "PytestPerfRegressionEvaluator"]
