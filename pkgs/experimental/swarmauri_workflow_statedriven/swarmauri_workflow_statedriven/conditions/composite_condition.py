# File: swarmauri/workflows/conditions/composite_condition.py

from typing import List, Dict, Any
from swarmauri_workflow_statedriven.conditions.base import Condition


class AndCondition(Condition):
    """
    File: swarmauri/workflows/conditions/composite_condition.py
    Class: AndCondition
    Method: __init__, evaluate
    """

    def __init__(self, conditions: List[Condition]):
        self.conditions = conditions

    def evaluate(self, state: Dict[str, Any]) -> bool:
        return all(cond.evaluate(state) for cond in self.conditions)


class OrCondition(Condition):
    """
    File: swarmauri/workflows/conditions/composite_condition.py
    Class: OrCondition
    Method: __init__, evaluate
    """

    def __init__(self, conditions: List[Condition]):
        self.conditions = conditions

    def evaluate(self, state: Dict[str, Any]) -> bool:
        return any(cond.evaluate(state) for cond in self.conditions)


class NotCondition(Condition):
    """
    File: swarmauri/workflows/conditions/composite_condition.py
    Class: NotCondition
    Method: __init__, evaluate
    """

    def __init__(self, condition: Condition):
        self.condition = condition

    def evaluate(self, state: Dict[str, Any]) -> bool:
        return not self.condition.evaluate(state)
