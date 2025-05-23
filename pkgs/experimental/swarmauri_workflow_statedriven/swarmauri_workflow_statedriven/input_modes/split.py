# swarmauri/workflows/input_modes/split.py

from typing import Any, Dict
from swarmauri_workflow_statedriven.input_modes.base import InputMode
from swarmauri_workflow_statedriven.state_manager import StateManager


class SplitInputMode(InputMode):
    """
    If the raw data is a list, split it into individual payloads.
    """

    def prepare(
        self,
        state_manager: StateManager,
        node_name: str,
        data: Any,
        results: Dict[str, Any],
    ) -> Any:
        """
        File: split.py
        Class: SplitInputMode
        Method: prepare

        If `data` is a list, enqueue each element back
        into the engine’s queue as its own (node_name, element)
        and return None to skip direct execution.
        Otherwise, return `data` unchanged.
        """
        if isinstance(data, list):
            # engine must detect None and not execute directly
            # and should re‑queue each element:
            for element in data:
                state_manager.enqueue((node_name, element))
            return None
        return data
