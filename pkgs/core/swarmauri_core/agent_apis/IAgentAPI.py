from abc import ABC, abstractmethod
from typing import Any, Coroutine, Dict


class IAgentAPI(ABC):

    @abstractmethod
    def invoke(self, agent_id: str, **kwargs: Dict[str, Any]) -> Any:
        """Invoke an agent synchronously."""
        pass

    @abstractmethod
    async def ainvoke(self, agent_id: str, **kwargs: Dict[str, Any]) -> Any:
        """Invoke an agent asynchronously."""
        pass
