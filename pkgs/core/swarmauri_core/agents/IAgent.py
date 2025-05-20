from abc import ABC, abstractmethod
from typing import Any, Optional, Dict, List, Union
from swarmauri_core.messages.IMessage import IMessage


class IAgent(ABC):
    @abstractmethod
    def exec(self, input_data: Optional[Any], llm_kwargs: Optional[Dict]) -> Any:
        """
        Executive method that triggers the agent's action based on the input data.
        """
        pass

    @abstractmethod
    async def aexec(
        self,
        input_str: Optional[Union[str, IMessage]] = "",
        llm_kwargs: Optional[Dict] = None,
    ) -> Any:
        """
        Async executive method that triggers the agent's action based on the input data.
        """
        pass

    @abstractmethod
    def batch(
        self,
        inputs: List[Union[str, IMessage]],
        llm_kwargs: Optional[Dict] = None,
    ) -> List[Any]:
        """
        Default batch implementation: calls `exec` on each input in `inputs`.
        Subclasses can override for optimized bulk behavior.
        """
        pass

    @abstractmethod
    async def abatch(
        self,
        inputs: List[Union[str, IMessage]],
        llm_kwargs: Optional[Dict] = None,
    ) -> List[Any]:
        """
        Default async batch implementation: concurrently calls `aexec` on all inputs.
        Subclasses can override for more efficient implementations.
        """
        pass
