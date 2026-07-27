"""Synchronous proxy for an async-native live session."""

import asyncio
from collections.abc import AsyncIterator, Iterator
from typing import Any, Awaitable, Callable

from swarmauri_core.live_models import ILiveConfig, ILiveInput, ILiveSession

from .LiveSessionRuntime import LiveSessionRuntime


class SyncLiveSessionBase(ILiveSession):
    def __init__(
        self,
        runtime: LiveSessionRuntime,
        session: ILiveSession,
    ) -> None:
        self._runtime = runtime
        self._session = session
        self._iterator: AsyncIterator[Any] | None = None
        self._closed = False

    @classmethod
    def create(
        cls,
        factory: Callable[[ILiveConfig], Awaitable[ILiveSession]],
        config: ILiveConfig,
    ) -> "SyncLiveSessionBase":
        runtime = LiveSessionRuntime()
        try:
            session = runtime.create(lambda: factory(config))
        except BaseException:
            runtime.close()
            raise
        return cls(runtime, session)

    @property
    def session_id(self) -> str:
        return self._session.session_id

    @property
    def state(self) -> str:
        return self._session.state

    @property
    def terminal_error(self) -> Any:
        return self._session.terminal_error

    def _ensure_runtime(self) -> None:
        if self._closed:
            raise RuntimeError("Live session is closed")

    def send(self, input_data: ILiveInput) -> None:
        self._ensure_runtime()
        self._runtime.submit(self._session.asend(input_data)).result()

    async def asend(self, input_data: ILiveInput) -> None:
        self._ensure_runtime()
        await asyncio.wrap_future(
            self._runtime.submit(self._session.asend(input_data))
        )

    def _next_event(self) -> Any:
        self._ensure_runtime()
        if self._iterator is None:
            self._iterator = self._session.astream()
        return self._runtime.submit(anext(self._iterator)).result()

    def stream(self) -> Iterator[Any]:
        while True:
            try:
                yield self._next_event()
            except StopAsyncIteration:
                return

    async def astream(self) -> AsyncIterator[Any]:
        while True:
            try:
                event = await asyncio.to_thread(self._next_event)
            except StopAsyncIteration:
                return
            yield event

    def wait_closed(self) -> None:
        self._ensure_runtime()
        self._runtime.submit(self._session.await_closed()).result()

    async def await_closed(self) -> None:
        self._ensure_runtime()
        await asyncio.wrap_future(
            self._runtime.submit(self._session.await_closed())
        )

    def close(self) -> None:
        if self._closed:
            return
        try:
            self._runtime.submit(self._session.aclose()).result()
        finally:
            self._closed = True
            self._runtime.close()

    async def aclose(self) -> None:
        if self._closed:
            return
        try:
            await asyncio.wrap_future(
                self._runtime.submit(self._session.aclose())
            )
        finally:
            self._closed = True
            await asyncio.to_thread(self._runtime.close)

    def __enter__(self) -> "SyncLiveSessionBase":
        return self

    def __exit__(self, *_: Any) -> None:
        self.close()
