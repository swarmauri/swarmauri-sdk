from typing import Literal

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_base.evaluator_pools.EvaluatorPoolBase import EvaluatorPoolBase


@ComponentBase.register_type(EvaluatorPoolBase, "EvaluatorPool")
class EvaluatorPool(EvaluatorPoolBase):
    """Concrete evaluator pool with no additional behavior."""

    type: Literal["EvaluatorPool"] = "EvaluatorPool"
