"""Base orchestration for realtime agents."""

from abc import abstractmethod
from collections.abc import AsyncIterator, Iterator
from typing import Any, Literal, Optional

from pydantic import ConfigDict, Field, PrivateAttr

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_base.conversations.ConversationBase import ConversationBase
from swarmauri_base.live_models.LiveConfigBase import LiveConfigBase
from swarmauri_base.live_models.LiveModelBase import LiveModelBase
from swarmauri_base.toolkits.ToolkitBase import ToolkitBase
from swarmauri_base.tools.ToolExecutorBase import ToolExecutorBase
from swarmauri_core.agents.IRealtimeAgent import IRealtimeAgent
from swarmauri_core.live_models.ILiveSession import ILiveSession

from .RealtimeInputAdapterBase import RealtimeInputAdapterBase
from .RealtimeOutputAdapterBase import RealtimeOutputAdapterBase


@ComponentBase.register_model()
class RealtimeAgentBase(IRealtimeAgent, ComponentBase):
    live_model: LiveModelBase
    config: LiveConfigBase = Field(default_factory=LiveConfigBase)
    conversation: Optional[ConversationBase] = None
    toolkit: Optional[ToolkitBase] = None
    tool_executor: ToolExecutorBase = Field(default_factory=ToolExecutorBase)
    input_adapter: Optional[RealtimeInputAdapterBase] = None
    output_adapter: Optional[RealtimeOutputAdapterBase] = None
    resource: str = Field(default=ResourceTypes.AGENT.value, frozen=True)
    type: Literal["RealtimeAgentBase"] = "RealtimeAgentBase"
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")
    _session: Optional[ILiveSession] = PrivateAttr(default=None)

    def connect(self, **kwargs: Any) -> ILiveSession:
        self._session = self.live_model.connect(self.config)
        return self._session

    async def aconnect(self, **kwargs: Any) -> ILiveSession:
        self._session = await self.live_model.aconnect(self.config)
        return self._session

    def send(self, input_data: Any) -> None:
        if self._session is None:
            self.connect()
        assert self._session is not None
        self._session.send(self._adapt_input(input_data))

    async def asend(self, input_data: Any) -> None:
        if self._session is None:
            await self.aconnect()
        assert self._session is not None
        await self._session.asend(self._adapt_input(input_data))

    def _adapt_input(self, input_data: Any) -> Any:
        return (
            self.input_adapter.adapt(input_data)
            if self.input_adapter
            else input_data
        )

    def stream(self) -> Iterator[Any]:
        if self._session is None:
            self.connect()
        assert self._session is not None
        yield from self._session.stream()

    async def astream(self) -> AsyncIterator[Any]:
        if self._session is None:
            await self.aconnect()
        assert self._session is not None
        async for event in self._session.astream():
            yield event

    @abstractmethod
    def run(self, *args: Any, **kwargs: Any) -> Any: ...

    @abstractmethod
    async def arun(self, *args: Any, **kwargs: Any) -> Any: ...

    def interrupt(self) -> None:
        from swarmauri_base.live_models.inputs import InterruptInput

        self.send(InterruptInput())

    async def ainterrupt(self) -> None:
        from swarmauri_base.live_models.inputs import InterruptInput

        await self.asend(InterruptInput())

    def close(self) -> None:
        if self._session is not None:
            self._session.close()
            self._session = None

    async def aclose(self) -> None:
        if self._session is not None:
            await self._session.aclose()
            self._session = None
