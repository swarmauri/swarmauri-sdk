from abc import ABC, abstractmethod
from typing import Any, List


class IControlPlane(ABC):
    """
    Abstract base class for ControlPlane.
    """

    @abstractmethod
    def create_agent(self, name: str, role: str) -> Any:
        """
        Create an agent with the given name and role.
        """
        pass

    @abstractmethod
    def distribute_tasks(self, task: Any) -> None:
        """
        Distribute tasks using the task strategy.
        """
        pass

    @abstractmethod
    def orchestrate_agents(self, task: Any) -> None:
        """
        Orchestrate agents for task distribution.
        """
        pass

    @abstractmethod
    def remove_agent(self, name: str) -> None:
        """
        Remove the agent with the specified name.
        """
        pass

    @abstractmethod
    def list_active_agents(self) -> List[str]:
        """
        List all active agent names.
        """
        pass
