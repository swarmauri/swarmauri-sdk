"""Awaitable-aware tool execution."""

import asyncio
import inspect
from concurrent.futures import Future
from typing import Any, Dict, Mapping, Optional

from pydantic import ConfigDict, Field, PrivateAttr

from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_core.tools.IToolExecutor import IToolExecutor

from .ToolExecutionPolicy import ToolExecutionPolicy
from .ToolExecutionResult import ToolExecutionResult


class ToolExecutorBase(IToolExecutor, ComponentBase):
    policy: ToolExecutionPolicy = Field(default_factory=ToolExecutionPolicy)
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")
    _running: Dict[str, Future[Any] | asyncio.Task[Any]] = PrivateAttr(
        default_factory=dict
    )

    @staticmethod
    def _invoke(tool: Any, arguments: Mapping[str, Any]) -> Any:
        target = getattr(tool, "call", tool)
        return target(**dict(arguments))

    def execute(
        self,
        tool: Any,
        arguments: Mapping[str, Any],
        *,
        call_id: Optional[str] = None,
        timeout: Optional[float] = None,
    ) -> ToolExecutionResult:
        result = self._invoke(tool, arguments)
        if inspect.isawaitable(result):
            try:
                asyncio.get_running_loop()
            except RuntimeError:
                result = asyncio.run(result)
            else:
                raise RuntimeError("Use aexecute() for an async tool")
        return ToolExecutionResult(call_id=call_id, value=result)

    async def aexecute(
        self,
        tool: Any,
        arguments: Mapping[str, Any],
        *,
        call_id: Optional[str] = None,
        timeout: Optional[float] = None,
    ) -> ToolExecutionResult:
        target = getattr(tool, "call", tool)
        if inspect.iscoroutinefunction(target):
            awaitable = target(**dict(arguments))
        else:
            result = await asyncio.to_thread(target, **dict(arguments))
            if inspect.isawaitable(result):
                awaitable = result
            else:
                return ToolExecutionResult(call_id=call_id, value=result)
        effective_timeout = timeout or self.policy.timeout
        value = (
            await asyncio.wait_for(awaitable, effective_timeout)
            if effective_timeout
            else await awaitable
        )
        return ToolExecutionResult(call_id=call_id, value=value)

    def cancel(self, call_id: str) -> bool:
        running = self._running.get(call_id)
        return bool(running and running.cancel())

    async def acancel(self, call_id: str) -> bool:
        return self.cancel(call_id)
