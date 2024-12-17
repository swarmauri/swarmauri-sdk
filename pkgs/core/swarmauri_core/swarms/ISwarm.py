from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union


class ISwarm(ABC):
    """Abstract base class for swarm implementations"""

    @abstractmethod
    async def exec(
        self,
        input_data: Union[str, List[str]],
        **kwargs: Dict[str, Any],
    ) -> Any:
        """Execute swarm tasks with given input"""
        pass

    @abstractmethod
    def get_swarm_status(self) -> Dict[int, Any]:
        """Get status of all agents in the swarm"""
        pass

    @property
    @abstractmethod
    def agents(self) -> List[Any]:
        """Get list of agents in the swarm"""
        pass

    @property
    @abstractmethod
    def queue_size(self) -> int:
        """Get size of task queue"""
        pass
