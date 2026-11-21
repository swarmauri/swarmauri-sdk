# File: swarmauri/workflows/transition.py

from typing import Any, Dict
from swarmauri_workflow_statedriven.conditions.base import Condition
from swarmauri_core.workflows import EdgeDefinition


class Transition:
    """Represents a directed edge between two workflow states, guarded by a
    Condition."""

    def __init__(
        self,
        source: str,
        target: str,
        condition: Condition,
        edge_id: str | None = None,
    ):
        """
        File: swarmauri/workflows/transition.py
        Class: Transition
        Method: __init__

        Args:
            source: the origin state name
            target: the destination state name
            condition: a Condition instance determining when this transition
            can fire
        """
        self.source = source
        self.target = target
        self.condition = condition
        self.edge_id = edge_id or f"{source}-to-{target}"

    @property
    def edge(self) -> EdgeDefinition:
        """Expose connectivity without treating a condition as authority."""
        return EdgeDefinition(self.edge_id, self.source, self.target)

    def is_triggered(self, state: Dict[str, Any]) -> bool:
        """
        File: swarmauri/workflows/transition.py
        Class: Transition
        Method: is_triggered

        Evaluate whether the transition should fire based on the current
        workflow state.

        Args:
            state: mapping of state names to their outputs

        Returns:
            True if the condition evaluates to True, False otherwise.
        """
        return self.condition.evaluate(state)
