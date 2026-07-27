"""Abstract agent implementations for the SwarmAuri SDK."""

import asyncio
from typing import Any, Literal, Union

from pydantic import ConfigDict, Field
from swarmauri_core.agents.IAgent import IAgent
from swarmauri_core.messages.IMessage import IMessage

from swarmauri_base.ComponentBase import (
    ComponentBase,
    ResourceTypes,
    SubclassUnion,
)
from swarmauri_base.llms.LLMBase import LLMBase


@ComponentBase.register_model()
class AgentBase(IAgent, ComponentBase):
    """
    File: AgentBase.py
    Class: AgentBase

    Base class for all agents. Supports single‐call (`exec`/`aexec`)
    and batch processing (`batch`/`abatch`).
    """

    llm: SubclassUnion[LLMBase]
    llm_kwargs: dict | None = {}
    resource: ResourceTypes = Field(default=ResourceTypes.AGENT.value)
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)
    type: Literal["AgentBase"] = "AgentBase"

    def exec(
        self,
        input_str: Union[str, IMessage] | None = "",
        llm_kwargs: dict | None = None,
    ) -> Any:
        """
        File: AgentBase.py
        Class: AgentBase
        Method: exec

        Synchronous single‐item execution. Subclasses must override.
        """
        raise NotImplementedError(
            "The `exec` method has not been implemented on this class."
        )

    async def aexec(
        self,
        input_str: Union[str, IMessage] | None = "",
        llm_kwargs: dict | None = None,
    ) -> Any:
        """
        File: AgentBase.py
        Class: AgentBase
        Method: aexec

        Asynchronous single‐item execution. Subclasses must override.
        """
        raise NotImplementedError(
            "The `aexec` method has not been implemented on this class."
        )

    def batch(
        self,
        inputs: list[Union[str, IMessage]],
        llm_kwargs: dict | None = None,
    ) -> list[Any]:
        """
        File: AgentBase.py
        Class: AgentBase
        Method: batch

        Default batch implementation: calls `exec` on each input in `inputs`.
        Subclasses can override for optimized bulk behavior.
        """
        llm_kwargs = llm_kwargs or self.llm_kwargs or {}
        results: list[Any] = []
        for inp in inputs:
            results.append(self.exec(inp, llm_kwargs=llm_kwargs))
        return results

    async def abatch(
        self,
        inputs: list[Union[str, IMessage]],
        llm_kwargs: dict | None = None,
    ) -> list[Any]:
        """
        File: AgentBase.py
        Class: AgentBase
        Method: abatch

        Default async batch implementation: concurrently calls `aexec` on all
        inputs.
        Subclasses can override for more efficient implementations.
        """
        llm_kwargs = llm_kwargs or self.llm_kwargs or {}
        tasks = [self.aexec(inp, llm_kwargs=llm_kwargs) for inp in inputs]
        return await asyncio.gather(*tasks)
