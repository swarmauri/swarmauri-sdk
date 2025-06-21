
"""Built-in fitness evaluators shipped with peagen."""

from .base import Evaluator
from .benchmark import PytestBenchmarkEvaluator
from .simple_time import SimpleTimeEvaluator


__all__ = ["Evaluator", "PytestBenchmarkEvaluator", "SimpleTimeEvaluator"]
