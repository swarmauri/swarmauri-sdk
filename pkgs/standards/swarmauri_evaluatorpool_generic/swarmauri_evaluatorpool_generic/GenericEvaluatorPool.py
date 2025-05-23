"""Generic evaluator pool implementation."""

from typing import Literal

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.evaluator_pools.EvaluatorPoolBase import EvaluatorPoolBase


@ComponentBase.register_type(EvaluatorPoolBase, "GenericEvaluatorPool")
class GenericEvaluatorPool(EvaluatorPoolBase):
    """A basic evaluator pool with no custom behaviour."""

    type: Literal["GenericEvaluatorPool"] = "GenericEvaluatorPool"
