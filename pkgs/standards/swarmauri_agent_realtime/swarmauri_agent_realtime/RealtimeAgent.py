from typing import Any, Literal

from swarmauri_base.agents import RealtimeAgentBase
from swarmauri_base.live_models.events import ToolCallEvent, TurnCompleteEvent

from .ConversationBridge import ConversationBridge
from .RealtimeToolCoordinator import RealtimeToolCoordinator


class RealtimeAgent(RealtimeAgentBase):
    type: Literal["RealtimeAgent"] = "RealtimeAgent"

    def run(self, input_data: Any, **kwargs: Any) -> list[Any]:
        async def _run() -> list[Any]:
            return await self.arun(input_data, **kwargs)

        from swarmauri_base.live_models.LiveSessionBase import LiveSessionBase

        return LiveSessionBase._run_sync(_run())

    async def arun(self, input_data: Any, **kwargs: Any) -> list[Any]:
        await self.asend(input_data)
        events: list[Any] = []
        coordinator = RealtimeToolCoordinator(self.tool_executor)
        async for event in self.astream():
            events.append(event)
            if isinstance(event, ToolCallEvent):
                result = await coordinator.handle(event, self.toolkit)
                await self.asend(result)
            if self.output_adapter is not None:
                await self.output_adapter.ahandle(event)
            if isinstance(event, TurnCompleteEvent):
                break
        ConversationBridge().append(self.conversation, events)
        return events
