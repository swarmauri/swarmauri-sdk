from abc import abstractmethod
from typing import List, Any, Literal, Optional

from pydantic import ConfigDict, Field
from swarmauri_core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.mas.IMas import IMas


class MasBase(IMas, ComponentBase):
    """Base class for a Multi-Agent System."""

    resource: Optional[str] = Field(default=ResourceTypes.MAS.value, frozen=True)
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)
    type: Literal["MasBase"] = "MasBase"

    @abstractmethod
    def add_agent(self, agent_id: str, agent: Any) -> None:
        """add an agent to the system."""
        raise NotImplementedError("Subclasses must implement the add_agent method.")

    @abstractmethod
    def remove_agent(self, agent_id: str) -> None:
        """remove an agent from the system."""
        raise NotImplementedError("Subclasses must implement the remove_agent method.")

    @abstractmethod
    def broadcast(self, message: Any) -> None:
        """send message to all agents in the system."""
        raise NotImplementedError("Subclasses must implement the broadcast method.")

    @abstractmethod
    def multicast(self, message: Any, recipient_ids: List[str]) -> None:
        """send message to a specific group of agents"""
        raise NotImplementedError("Subclasses must implement the multicast method.")

    @abstractmethod
    def unicast(self, message: Any, recipient_id: str) -> None:
        """send message to a single agent."""
        raise NotImplementedError("Subclasses must implement the unicast method.")

    @abstractmethod
    def dispatch_task(self, task: Any, agent_id: str) -> None:
        """assign a single task to a specific agent."""
        raise NotImplementedError("Subclasses must implement the dispatch_task method.")

    @abstractmethod
    def dispatch_tasks(self, tasks: List[Any], agent_ids: List[str]) -> None:
        """assign multiple tasks to multiple agents."""
        raise NotImplementedError(
            "Subclasses must implement the dispatch_tasks method."
        )
