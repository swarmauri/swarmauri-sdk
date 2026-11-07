from typing import Any, Literal

from pydantic import ConfigDict, Field
from swarmauri_core.state.IState import IState

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes


@ComponentBase.register_model()
class StateBase(IState, ComponentBase):
    """
    Abstract base class for state management, extending IState and
    ComponentBase.
    """

    state_data: dict[str, Any] = Field(
        default_factory=dict, description="The current state data."
    )
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)
    resource: str | None = Field(
        default=ResourceTypes.STATE.value, frozen=True
    )
    type: Literal["StateBase"] = "StateBase"

    def read(self) -> dict[str, Any]:
        """
        Reads and returns the current state as a dictionary.
        """
        raise NotImplementedError("Subclasses must implement 'read'.")

    def write(self, data: dict[str, Any]) -> None:
        """
        Replaces the current state with the given data.
        """
        raise NotImplementedError("Subclasses must implement 'write'.")

    def update(self, data: dict[str, Any]) -> None:
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
