from typing import Dict, Any, Optional, Literal
from pydantic import Field, ConfigDict
from swarmauri_core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.state.IState import IState


class StateBase(IState, ComponentBase):
    """
    Abstract base class for state management, extending IState and ComponentBase.
    """

    state_data: Dict[str, Any] = Field(
        default_factory=dict, description="The current state data."
    )
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)
    resource: Optional[str] = Field(default=ResourceTypes.STATE.value, frozen=True)
    type: Literal["StateBase"] = "StateBase"

    def read(self) -> Dict[str, Any]:
        """
        Reads and returns the current state as a dictionary.
        """
        raise NotImplementedError("Subclasses must implement 'read'.")

    def write(self, data: Dict[str, Any]) -> None:
        """
        Replaces the current state with the given data.
        """
        raise NotImplementedError("Subclasses must implement 'write'.")

    def update(self, data: Dict[str, Any]) -> None:
        """
        Updates the state with the given data.
        """
        raise NotImplementedError("Subclasses must implement 'update'.")

    def reset(self) -> None:
        """
        Resets the state to its initial state.
        """
        raise NotImplementedError("Subclasses must implement 'reset'.")

    def deep_copy(self) -> "IState":
        """
        Creates a deep copy of the current state.
        """
        raise NotImplementedError("Subclasses must implement 'deep_copy'.")
