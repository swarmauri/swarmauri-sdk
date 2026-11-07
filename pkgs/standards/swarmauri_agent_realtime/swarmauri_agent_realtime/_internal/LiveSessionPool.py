import asyncio
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from time import monotonic
from typing import Any

from .LiveSessionEntry import LiveSessionEntry

SessionFactory = Callable[[], Awaitable[Any]]


class LiveSessionPool:
    """Lease-based pool with one live session per conversation."""

    def __init__(
        self, max_sessions: int = 32, idle_timeout: float = 300.0
    ) -> None:
        if max_sessions < 1:
            raise ValueError("max_sessions must be positive")
        self.max_sessions = max_sessions
        self.idle_timeout = idle_timeout
        self._entries: dict[str, LiveSessionEntry] = {}
        self._lock = asyncio.Lock()

    async def acquire(
        self, conversation_id: str, factory: SessionFactory
    ) -> Any:
        close_after: list[Any] = []
        async with self._lock:
            now = monotonic()
            for key, entry in list(self._entries.items()):
                if (
                    entry.leases == 0
                    and now - entry.last_used_at >= self.idle_timeout
                ):
                    self._entries.pop(key)
                    entry.invalidated = True
                    if entry.session is not None:
                        close_after.append(entry.session)
            entry = self._entries.get(conversation_id)
            if entry is None:
                idle = sorted(
                    (
                        item
                        for item in self._entries.values()
                        if item.leases == 0
                    ),
                    key=lambda item: item.last_used_at,
                )
                while len(self._entries) >= self.max_sessions and idle:
                    expired = idle.pop(0)
                    self._entries.pop(expired.conversation_id, None)
                    expired.invalidated = True
                    if expired.session is not None:
                        close_after.append(expired.session)
                if len(self._entries) >= self.max_sessions:
                    raise RuntimeError(
                        "All live sessions are currently leased"
                    )
                entry = LiveSessionEntry(
                    conversation_id=conversation_id,
                    creation_task=asyncio.create_task(factory()),
                    last_used_at=now,
                )
                self._entries[conversation_id] = entry
            task = entry.creation_task

        await asyncio.gather(
            *(session.aclose() for session in close_after),
            return_exceptions=True,
        )
        try:
            session = await task
        except BaseException:
            async with self._lock:
                if self._entries.get(conversation_id) is entry:
                    self._entries.pop(conversation_id, None)
            raise

        invalidated = False
        async with self._lock:
            invalidated = entry.invalidated
            if not invalidated:
                entry.session = session
                entry.leases += 1
                entry.last_used_at = monotonic()
        if invalidated:
            await session.aclose()
            raise RuntimeError("Live session was invalidated during creation")
        return session

    async def release(
        self, conversation_id: str, *, invalidate: bool = False
    ) -> None:
        close_session: Any | None = None
        async with self._lock:
            entry = self._entries.get(conversation_id)
            if entry is None:
                return
            entry.leases = max(0, entry.leases - 1)
            entry.last_used_at = monotonic()
            if invalidate:
                entry.invalidated = True
            if entry.invalidated and entry.leases == 0:
                self._entries.pop(conversation_id, None)
                close_session = entry.session
        if close_session is not None:
            await close_session.aclose()

    @asynccontextmanager
    async def session(
        self,
        conversation_id: str,
        factory: SessionFactory,
    ) -> AsyncIterator[Any]:
        session = await self.acquire(conversation_id, factory)
        invalidate = False
        try:
            yield session
        except BaseException:
            invalidate = True
            raise
        finally:
            await self.release(conversation_id, invalidate=invalidate)

    async def invalidate(self, conversation_id: str) -> None:
        await self.release(conversation_id, invalidate=True)

    async def close_all(self) -> None:
        async with self._lock:
            entries = list(self._entries.values())
            self._entries.clear()
            for entry in entries:
                entry.invalidated = True
        for entry in entries:
            if not entry.creation_task.done():
                entry.creation_task.cancel()
            if entry.session is not None:
                await entry.session.aclose()

    async def size(self) -> int:
        async with self._lock:
            return len(self._entries)
