from abc import ABC, abstractmethod
from typing import Any, Union

from swarmauri_core.messages.IMessage import IMessage


class IAgent(ABC):
    @abstractmethod
    def exec(self, input_data: Any | None, llm_kwargs: dict | None) -> Any:
        """
        Executive method that triggers the agent's action based on the input
        data.
        """

    @abstractmethod
    async def aexec(
        self,
        input_str: Union[str, IMessage] | None = "",
        llm_kwargs: dict | None = None,
    ) -> Any:
        """
        Async executive method that triggers the agent's action based on the
        input data.
        """

    @abstractmethod
    def batch(
        self,
        inputs: list[Union[str, IMessage]],
        llm_kwargs: dict | None = None,
    ) -> list[Any]:
        """
        Default batch implementation: calls `exec` on each input in `inputs`.
        Subclasses can override for optimized bulk behavior.
        """

    @abstractmethod
    async def abatch(
        self,
        inputs: list[Union[str, IMessage]],
        llm_kwargs: dict | None = None,
    ) -> list[Any]:
        """
        Default async batch implementation: concurrently calls `aexec` on all
        inputs.
        Subclasses can override for more efficient implementations.
        """
