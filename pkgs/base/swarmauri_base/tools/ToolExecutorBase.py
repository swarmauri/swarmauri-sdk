"""Policy-aware sync and async tool execution."""

import asyncio
import inspect
import threading
from collections.abc import Mapping
from concurrent.futures import Future, ThreadPoolExecutor, TimeoutError
from typing import Any

from pydantic import ConfigDict, Field, PrivateAttr
from swarmauri_core.tools.IToolExecutor import IToolExecutor

from swarmauri_base.ComponentBase import ComponentBase

from .ToolExecutionError import (
    DuplicateToolCallError,
    ToolApprovalDeniedError,
    ToolApprovalRequiredError,
    ToolExecutionTimeoutError,
)
from .ToolExecutionPolicy import ToolExecutionPolicy
from .ToolExecutionRequest import ToolExecutionRequest
from .ToolExecutionResult import ToolExecutionResult


class ToolExecutorBase(IToolExecutor, ComponentBase):
    policy: ToolExecutionPolicy = Field(default_factory=ToolExecutionPolicy)
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")
    _running: dict[str, Future[Any] | asyncio.Task[Any]] = PrivateAttr(
        default_factory=dict
    )
    _running_lock: threading.RLock = PrivateAttr(
        default_factory=threading.RLock
    )
    _thread_pool: ThreadPoolExecutor = PrivateAttr(
        default_factory=ThreadPoolExecutor
    )

    @staticmethod
    def _target(tool: Any) -> Any:
        return getattr(tool, "call", tool)

    @classmethod
    def _request(
        cls,
        tool: Any,
        arguments: Mapping[str, Any],
        call_id: str | None,
        context: Mapping[str, Any] | None,
    ) -> ToolExecutionRequest:
        execution_context = dict(context or {})
        return ToolExecutionRequest(
            call_id=call_id,
            tool_name=str(
                getattr(
                    tool,
                    "name",
                    getattr(tool, "__name__", type(tool).__name__),
                )
            ),
            arguments=dict(arguments),
            session_id=execution_context.get("session_id"),
            conversation_id=execution_context.get("conversation_id"),
            provider_name=execution_context.get("provider_name"),
            correlation=dict(execution_context.get("correlation") or {}),
        )

    def _register(self, call_id: str | None, operation: Any) -> None:
        if call_id is None:
            return
        with self._running_lock:
            if call_id in self._running:
                raise DuplicateToolCallError(
                    f"Tool call {call_id!r} is already active"
                )
            self._running[call_id] = operation

    def _unregister(self, call_id: str | None, operation: Any) -> None:
        if call_id is None:
            return
        with self._running_lock:
            if self._running.get(call_id) is operation:
                self._running.pop(call_id, None)

    def _approve(self, request: ToolExecutionRequest) -> bool:
        if not self.policy.require_approval:
            return True
        callback = self.policy.approval_callback
        if callback is None:
            return not self.policy.deny_without_callback
        decision = callback(request)
        if inspect.isawaitable(decision):
            try:
                asyncio.get_running_loop()
            except RuntimeError:
                decision = asyncio.run(decision)
            else:
                raise RuntimeError(
                    "Use aexecute() with an async approval callback"
                )
        return bool(decision)

    async def _aapprove(self, request: ToolExecutionRequest) -> bool:
        if not self.policy.require_approval:
            return True
        callback = self.policy.approval_callback
        if callback is None:
            return not self.policy.deny_without_callback
        decision = callback(request)
        if inspect.isawaitable(decision):
            decision = await decision
        return bool(decision)

    @staticmethod
    def _denied(
        request: ToolExecutionRequest, missing: bool = False
    ) -> ToolExecutionResult:
        error = (
            ToolApprovalRequiredError("Tool approval callback is required")
            if missing
            else ToolApprovalDeniedError("Tool execution was denied")
        )
        return ToolExecutionResult(
            call_id=request.call_id,
            tool_name=request.tool_name,
            status="denied",
            error=str(error),
        )

    def execute(
        self,
        tool: Any,
        arguments: Mapping[str, Any],
        *,
        call_id: str | None = None,
        timeout: float | None = None,
        context: Mapping[str, Any] | None = None,
    ) -> ToolExecutionResult:
        request = self._request(tool, arguments, call_id, context)
        try:
            approved = self._approve(request)
        except Exception as exc:
            return ToolExecutionResult(
                call_id=call_id,
                tool_name=request.tool_name,
                status="failed",
                error=str(exc),
            )
        if not approved:
            return self._denied(request, self.policy.approval_callback is None)

        def invoke() -> Any:
            result = self._target(tool)(**dict(arguments))
            return (
                asyncio.run(result) if inspect.isawaitable(result) else result
            )

        future = self._thread_pool.submit(invoke)
        try:
            self._register(call_id, future)
            value = future.result(
                timeout=timeout if timeout is not None else self.policy.timeout
            )
            return ToolExecutionResult(
                call_id=call_id, tool_name=request.tool_name, value=value
            )
        except DuplicateToolCallError as exc:
            future.cancel()
            return ToolExecutionResult(
                call_id=call_id,
                tool_name=request.tool_name,
                status="failed",
                error=str(exc),
            )
        except TimeoutError:
            future.cancel()
            error = ToolExecutionTimeoutError("Tool execution timed out")
            return ToolExecutionResult(
                call_id=call_id,
                tool_name=request.tool_name,
                status="timed_out",
                error=str(error),
            )
        except Exception as exc:
            return ToolExecutionResult(
                call_id=call_id,
                tool_name=request.tool_name,
                status="failed",
                error=str(exc),
            )
        finally:
            self._unregister(call_id, future)

    async def aexecute(
        self,
        tool: Any,
        arguments: Mapping[str, Any],
        *,
        call_id: str | None = None,
        timeout: float | None = None,
        context: Mapping[str, Any] | None = None,
    ) -> ToolExecutionResult:
        request = self._request(tool, arguments, call_id, context)
        try:
            approved = await self._aapprove(request)
        except Exception as exc:
            return ToolExecutionResult(
                call_id=call_id,
                tool_name=request.tool_name,
                status="failed",
                error=str(exc),
            )
        if not approved:
            return self._denied(request, self.policy.approval_callback is None)

        async def invoke() -> Any:
            target = self._target(tool)
            if inspect.iscoroutinefunction(target):
                return await target(**dict(arguments))
            result = await asyncio.to_thread(target, **dict(arguments))
            return await result if inspect.isawaitable(result) else result

        task = asyncio.create_task(invoke())
        try:
            self._register(call_id, task)
            effective_timeout = (
                timeout if timeout is not None else self.policy.timeout
            )
            value = (
                await asyncio.wait_for(task, effective_timeout)
                if effective_timeout
                else await task
            )
            return ToolExecutionResult(
                call_id=call_id, tool_name=request.tool_name, value=value
            )
        except DuplicateToolCallError as exc:
            task.cancel()
            return ToolExecutionResult(
                call_id=call_id,
                tool_name=request.tool_name,
                status="failed",
                error=str(exc),
            )
        except asyncio.TimeoutError:
            error = ToolExecutionTimeoutError("Tool execution timed out")
            return ToolExecutionResult(
                call_id=call_id,
                tool_name=request.tool_name,
                status="timed_out",
                error=str(error),
            )
        except asyncio.CancelledError:
            return ToolExecutionResult(
                call_id=call_id,
                tool_name=request.tool_name,
                status="cancelled",
                cancelled=True,
            )
        except Exception as exc:
            return ToolExecutionResult(
                call_id=call_id,
                tool_name=request.tool_name,
                status="failed",
                error=str(exc),
            )
        finally:
            self._unregister(call_id, task)

    def cancel(self, call_id: str) -> bool:
        with self._running_lock:
            running = self._running.get(call_id)
        if running is None or running.done():
            return False
        if isinstance(running, asyncio.Task):
            running.get_loop().call_soon_threadsafe(running.cancel)
            return True
        return running.cancel()

    async def acancel(self, call_id: str) -> bool:
        return self.cancel(call_id)
