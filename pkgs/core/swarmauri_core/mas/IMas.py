from typing import List, Any
from abc import ABC, abstractmethod


class IMas(ABC):
    @abstractmethod
    def broadcast(self, message: Any) -> None:
        """Send message to all agents in the system."""
        pass

    @abstractmethod
    def multicast(self, message: Any, recipient_ids: List[str]) -> None:
        """Send message to a specific group of agents."""
        pass

    @abstractmethod
    def unicast(self, message: Any, recipient_id: str) -> None:
        """Send message to a single agent."""
        pass

    @abstractmethod
    def dispatch_task(self, task: Any, agent_id: str) -> None:
        """Assign a single task to a specific agent."""
        pass

    @abstractmethod
    def dispatch_tasks(self, tasks: List[Any], agent_ids: List[str]) -> None:
        """Assign multiple tasks to multiple agents."""
        pass

    @abstractmethod
    def add_agent(self, agent_id: str, agent: Any) -> None:
        """Add an agent to the system."""
        pass

    @abstractmethod
    def remove_agent(self, agent_id: str) -> None:
        """Remove an agent from the system."""
        pass
