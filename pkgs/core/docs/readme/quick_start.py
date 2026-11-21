import asyncio
from typing import Any, Optional

from swarmauri_core.agents.IAgent import IAgent
from swarmauri_core.messages.IMessage import IMessage


class MinimalAgent(IAgent):
    def exec(
        self,
        input_data: Optional[Any] = None,
        llm_kwargs: Optional[dict] = None,
    ) -> Any:
        return {"input": input_data, "kwargs": llm_kwargs or {}}

    async def aexec(
        self,
        input_str: Optional[str | IMessage] = "",
        llm_kwargs: Optional[dict] = None,
    ) -> Any:
        return self.exec(input_str, llm_kwargs)

    def batch(
        self,
        inputs: list[str | IMessage],
        llm_kwargs: Optional[dict] = None,
    ) -> list[Any]:
        return [self.exec(item, llm_kwargs) for item in inputs]

    async def abatch(
        self,
        inputs: list[str | IMessage],
        llm_kwargs: Optional[dict] = None,
    ) -> list[Any]:
        return await asyncio.gather(
            *(self.aexec(item, llm_kwargs) for item in inputs)
        )
