# File: swarmauri/workflows/state_manager.py

from typing import Any, Dict, List
from swarmauri_workflow_statedriven.exceptions import WorkflowError


class StateManager:
    """
    File: swarmauri/workflows/state_manager.py
    Class: StateManager
    Methods:
        - __init__
        - update_state
        - get_state
        - buffer_input
        - get_buffer
        - pop_buffer
        - log
    """

    def __init__(self):
        """
        File: swarmauri/workflows/state_manager.py
        Class: StateManager
        Method: __init__

        Initialize containers for state values, logs, and join buffers.
        """
        self.state: Dict[str, Any] = {}
        self.logs: List[str] = []
        self.join_buffers: Dict[str, List[Any]] = {}

    def update_state(self, name: str, value: Any) -> None:
        """
        File: swarmauri/workflows/state_manager.py
        Class: StateManager
        Method: update_state

        Store the given value as the current output for state `name`.
        """
        self.state[name] = value

    def get_state(self, name: str) -> Any:
        """
        File: swarmauri/workflows/state_manager.py
        Class: StateManager
        Method: get_state

        Retrieve the stored output for state `name`. Raises if not found.
        """
        if name not in self.state:
            raise WorkflowError(f"State '{name}' has no recorded value")
        return self.state[name]

    def buffer_input(self, target: str, value: Any) -> None:
        """
        File: swarmauri/workflows/state_manager.py
        Class: StateManager
        Method: buffer_input

        Buffer an incoming value for a join on `target`.
        """
        self.join_buffers.setdefault(target, []).append(value)

    def get_buffer(self, target: str) -> List[Any]:
        """
        File: swarmauri/workflows/state_manager.py
        Class: StateManager
        Method: get_buffer

        Return the list of buffered inputs for `target`, without clearing.
        """
        return self.join_buffers.get(target, [])

    def pop_buffer(self, target: str) -> List[Any]:
        """
        File: swarmauri/workflows/state_manager.py
        Class: StateManager
        Method: pop_buffer

        Return and clear buffered inputs for `target`.
        """
        return self.join_buffers.pop(target, [])

    def log(self, message: str) -> None:
        """
        File: swarmauri/workflows/state_manager.py
        Class: StateManager
        Method: log

        Append message to logs.
        """
        self.logs.append(message)
