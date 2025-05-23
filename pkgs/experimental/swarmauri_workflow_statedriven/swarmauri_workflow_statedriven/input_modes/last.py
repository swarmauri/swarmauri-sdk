# File: swarmauri/workflows/input_modes/last.py

from typing import Any, Dict
from swarmauri_workflow_statedriven.input_modes.base import InputMode
from swarmauri_workflow_statedriven.state_manager import StateManager


class LastInputMode(InputMode):
    """
    File: last.py
    Class: LastInputMode
    Method: prepare

    If the raw data is a list, return its last element; otherwise return it unchanged.
    """

    def prepare(
        self,
        state_manager: StateManager,
        node_name: str,
        data: Any,
        results: Dict[str, Any],
    ) -> Any:
        """
        Return data[-1] if data is a non-empty list; else return data.
        """
        if isinstance(data, list):
            return data[-1] if data else None
        return data
