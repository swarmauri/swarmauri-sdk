# swarmauri/workflows/input_modes/base.py

from abc import ABC, abstractmethod
from typing import Any, Dict
from swarmauri_workflow_statedriven.state_manager import StateManager


class InputMode(ABC):
    """
    Base for all input‑mode strategies:
    decide what data a node sees before execution.
    """

    @abstractmethod
    def prepare(
        self,
        state_manager: StateManager,
        node_name: str,
        data: Any,
        results: Dict[str, Any],
    ) -> Any:
        """
        Produce the actual input for node.execute()/batch().

        Args:
            state_manager: the workflow’s StateManager.
            node_name: name of the node about to run.
            data: raw dequeued payload.
            results: all completed outputs so far.

        Returns:
            Either a scalar or a list of scalars/dicts.
        """
        ...
