from typing import Any

from swarmauri_base.live_models.events import ToolCallEvent
from swarmauri_base.live_models.inputs import ToolResultInput
from swarmauri_base.tools import ToolExecutorBase


class RealtimeToolCoordinator:
    def __init__(self, executor: ToolExecutorBase) -> None:
        self.executor = executor

    @staticmethod
    def find_tool(toolkit: Any, name: str) -> Any:
        if toolkit is None:
            raise KeyError(f"No toolkit configured for tool {name!r}")
        if hasattr(toolkit, "get_tool_by_name"):
            return toolkit.get_tool_by_name(name)
        tools = getattr(toolkit, "tools", toolkit)
        if isinstance(tools, dict):
            return tools[name]
        for tool in tools:
            if getattr(tool, "name", None) == name:
                return tool
        raise KeyError(name)

    async def handle(
        self, event: ToolCallEvent, toolkit: Any
    ) -> ToolResultInput:
        try:
            tool = self.find_tool(toolkit, event.tool_name)
            result = await self.executor.aexecute(
                tool,
                event.arguments,
                call_id=event.call_id,
            )
            return ToolResultInput(
                call_id=event.call_id,
                correlation_id=event.tool_name,
                payload=result.value,
                is_error=bool(result.error),
            )
        except Exception as exc:
            return ToolResultInput(
                call_id=event.call_id,
                correlation_id=event.tool_name,
                payload={"error": str(exc)},
                is_error=True,
            )
