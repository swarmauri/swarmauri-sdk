# File: swarmauri/workflows/input_modes/identity.py

from typing import Any, Dict
from swarmauri_workflow_statedriven.input_modes.base import InputMode
from swarmauri_workflow_statedriven.state_manager import StateManager


class IdentityInputMode(InputMode):
    """
    File: input_modes/identity.py
    Class: IdentityInputMode
    Method: prepare

    Passes the incoming data through unchanged, whether scalar or list.
    """

    def prepare(
        self,
        state_manager: StateManager,
        node_name: str,
        data: Any,
        results: Dict[str, Any],
    ) -> Any:
        """
        Return the raw payload exactly as received.
        """
        return data
