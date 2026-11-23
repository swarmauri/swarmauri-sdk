from abc import ABC, abstractmethod
from typing import Any, Union


class ISwarm(ABC):
    """Abstract base class for swarm implementations"""

    @abstractmethod
    async def exec(
        self,
        input_data: Union[str, list[str]],
        **kwargs: dict[str, Any],
    ) -> Any:
        """Execute swarm tasks with given input"""

    @abstractmethod
    def get_swarm_status(self) -> dict[int, Any]:
        """Get status of all agents in the swarm"""

    @property
    @abstractmethod
    def agents(self) -> list[Any]:
        """Get list of agents in the swarm"""

    @property
    @abstractmethod
    def queue_size(self) -> int:
        """Get size of task queue"""
