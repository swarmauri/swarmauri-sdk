# swarmauri/workflows/input_modes/aggregate.py

from typing import Any, Dict
from swarmauri_workflow_statedriven.input_modes.base import InputMode
from swarmauri_workflow_statedriven.state_manager import StateManager


class AggregateInputMode(InputMode):
    """
    Pass the full map of all prior state outputs as input.
    """

    def prepare(
        self,
        state_manager: StateManager,
        node_name: str,
        data: Any,
        results: Dict[str, Any],
    ) -> Any:
        """
        File: aggregate.py
        Class: AggregateInputMode
        Method: prepare

        Returns a shallow copy of `results` so the node sees every completed output.
        """
        return results.copy()
