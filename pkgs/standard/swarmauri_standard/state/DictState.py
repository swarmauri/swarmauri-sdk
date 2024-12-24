from typing import Dict, Any
from copy import deepcopy
from pydantic import Field, model_validator
from swarmauri_base.state.StateBase import StateBase


class DictState(StateBase):
    """
    A concrete implementation of StateBase that manages state as a dictionary.
    """

    state_data: Dict[str, Any] = Field(
        default_factory=dict, description="The current state data."
    )

    def read(self) -> Dict[str, Any]:
        """
        Reads and returns the current state as a dictionary.
        """
        return deepcopy(self.state_data)

    def write(self, data: Dict[str, Any]) -> None:
        """
        Replaces the current state with the given data.
        """
        self.state_data = deepcopy(data)

    def update(self, data: Dict[str, Any]) -> None:
        """
        Updates the state with the given data.
        """
        self.state_data.update(data)

    def reset(self) -> None:
        """
        Resets the state to an empty dictionary.
        """
        self.state_data = {}

    def deep_copy(self) -> "DictState":
        """
        Creates a deep copy of the current state.
        """
        return DictState(state_data=deepcopy(self.state_data))

    @model_validator(mode="after")
    def _ensure_deep_copy(self):
        # Ensures that state_data is always a deep copy
        self.state_data = deepcopy(self.state_data)
        return self
