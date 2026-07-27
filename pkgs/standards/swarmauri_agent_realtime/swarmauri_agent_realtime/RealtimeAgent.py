from typing import Any, Literal

from swarmauri_base.agents import RealtimeAgentBase
from swarmauri_base.live_models.events import (
    ToolCallEvent,
    ToolCancellationEvent,
    TurnCompleteEvent,
)

from .RealtimeAgentRunResult import RealtimeAgentRunResult
from ._internal.RealtimeToolCoordinator import RealtimeToolCoordinator
from ._internal.RealtimeTurnAccumulator import RealtimeTurnAccumulator
from ._internal.SwarmauriConversationAdapter import (
    SwarmauriConversationAdapter,
)


class RealtimeAgent(RealtimeAgentBase):
    type: Literal["RealtimeAgent"] = "RealtimeAgent"

    def run(self, input_data: Any, **kwargs: Any) -> RealtimeAgentRunResult:
        self.send(input_data)
        events: list[Any] = []
        accumulator = RealtimeTurnAccumulator()
        turn = accumulator.turn
        coordinator = RealtimeToolCoordinator(self.tool_executor, self.toolkit)
        for event in self.stream():
            events.append(event)
            turn = accumulator.consume(event)
            if isinstance(event, ToolCallEvent):
                self.send(coordinator.handle_call(event))
            elif isinstance(event, ToolCancellationEvent):
                coordinator.handle_cancellation(event)
            if self.output_adapter is not None:
                self.output_adapter.handle(event)
            if isinstance(event, TurnCompleteEvent):
                break
        SwarmauriConversationAdapter().append_turn(self.conversation, turn)
        return RealtimeAgentRunResult(turn=turn, events=events)

    async def arun(
        self,
        input_data: Any,
        **kwargs: Any,
    ) -> RealtimeAgentRunResult:
        await self.asend(input_data)
        events: list[Any] = []
        accumulator = RealtimeTurnAccumulator()
        turn = accumulator.turn
        coordinator = RealtimeToolCoordinator(self.tool_executor, self.toolkit)
        async for event in self.astream():
            events.append(event)
            turn = accumulator.consume(event)
            if isinstance(event, ToolCallEvent):
                await self.asend(await coordinator.ahandle_call(event))
            elif isinstance(event, ToolCancellationEvent):
                await coordinator.ahandle_cancellation(event)
            if self.output_adapter is not None:
                await self.output_adapter.ahandle(event)
            if isinstance(event, TurnCompleteEvent):
                break
        SwarmauriConversationAdapter().append_turn(self.conversation, turn)
        return RealtimeAgentRunResult(turn=turn, events=events)
