
from swarmauri_base.live_models.events.ToolCallEvent import ToolCallEvent
from swarmauri_base.live_models.events.ToolCancellationEvent import (
    ToolCancellationEvent,
)
from swarmauri_base.live_models.inputs.ToolResultInput import ToolResultInput
from swarmauri_base.tools.ToolExecutorBase import ToolExecutorBase
from swarmauri_core.toolkits.IToolkit import IToolkit


class RealtimeToolCoordinator:
    def __init__(
        self, executor: ToolExecutorBase, toolkit: IToolkit | None
    ) -> None:
        self.executor = executor
        self.toolkit = toolkit

    def _tool(self, name: str):
        if self.toolkit is None:
            raise KeyError(f"No toolkit configured for tool {name!r}")
        tool = self.toolkit.get_tool_by_name(name)
        if tool is None:
            raise KeyError(name)
        return tool

    @staticmethod
    def _input(event: ToolCallEvent, result) -> ToolResultInput:
        correlation_id = event.correlation.get("provider_event_id")
        return ToolResultInput(
            call_id=event.call_id,
            correlation_id=correlation_id,
            payload=result.value
            if not result.error
            else {"error": result.error},
            is_error=bool(result.error),
        )

    def handle_call(self, event: ToolCallEvent) -> ToolResultInput:
        try:
            result = self.executor.execute(
                self._tool(event.tool_name),
                event.arguments,
                call_id=event.call_id,
                context={"correlation": event.correlation},
            )
        except Exception as exc:
            return ToolResultInput(
                call_id=event.call_id,
                correlation_id=event.correlation.get("provider_event_id"),
                payload={"error": str(exc)},
                is_error=True,
            )
        return self._input(event, result)

    async def ahandle_call(self, event: ToolCallEvent) -> ToolResultInput:
        try:
            result = await self.executor.aexecute(
                self._tool(event.tool_name),
                event.arguments,
                call_id=event.call_id,
                context={"correlation": event.correlation},
            )
        except Exception as exc:
            return ToolResultInput(
                call_id=event.call_id,
                correlation_id=event.correlation.get("provider_event_id"),
                payload={"error": str(exc)},
                is_error=True,
            )
        return self._input(event, result)

    def handle_cancellation(self, event: ToolCancellationEvent) -> bool:
        return self.executor.cancel(event.call_id)

    async def ahandle_cancellation(self, event: ToolCancellationEvent) -> bool:
        return await self.executor.acancel(event.call_id)
