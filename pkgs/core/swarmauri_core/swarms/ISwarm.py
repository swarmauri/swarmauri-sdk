from abc import ABC, abstractmethod
from typing import Any, List, Tuple


class ISwarm(ABC):
    """Abstract interface for swarm implementations with both sync/async operations."""

    @property
    @abstractmethod
    def num_agents(self) -> int:
        """Number of agents in the swarm."""
        pass

    @abstractmethod
    def add_agent(self, agent: Any) -> None:
        """Add an agent to the swarm."""
        pass

    @abstractmethod
    def remove_agent(self, agent_id: int) -> None:
        """Remove an agent from the swarm."""
        pass

    @abstractmethod
    def replace_agent(self, agent_id: int, new_agent: Any) -> None:
        """Replace an agent in the swarm."""
        pass

    @abstractmethod
    def get_agent_statuses(self) -> List[Tuple[int, Any]]:
        """Get status of all agents."""
        pass

    @abstractmethod
    def distribute_task(self, task: Any) -> None:
        """Distribute a task to the swarm."""
        pass

    @abstractmethod
    def collect_results(self) -> List[Any]:
        """Collect results from the swarm."""
        pass

    @abstractmethod
    def run(self, tasks: List[Any]) -> List[Any]:
        """Execute tasks synchronously."""
        pass

    @abstractmethod
    async def arun(self, tasks: List[Any]) -> List[Any]:
        """Execute tasks asynchronously."""
        pass

    @abstractmethod
    def process_task(self, task: Any) -> Any:
        """Process a single task synchronously."""
        pass

    @abstractmethod
    async def aprocess_task(self, task: Any) -> Any:
        """Process a single task asynchronously."""
        pass
