"""Built-in fitness evaluators for Peagen."""

from .base import Evaluator
from .simple_time import SimpleTimeEvaluator

__all__ = ["Evaluator", "SimpleTimeEvaluator"]
