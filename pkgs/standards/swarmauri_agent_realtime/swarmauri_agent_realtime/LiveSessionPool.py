import asyncio
from collections import OrderedDict
from typing import Any, Optional


class LiveSessionPool:
    """One live provider connection per conversation."""

    def __init__(self, max_sessions: int = 32) -> None:
        self.max_sessions = max_sessions
        self._sessions: OrderedDict[str, Any] = OrderedDict()
        self._lock = asyncio.Lock()

    async def acquire(self, conversation_id: str, factory: Any) -> Any:
        async with self._lock:
            if conversation_id in self._sessions:
                session = self._sessions.pop(conversation_id)
                self._sessions[conversation_id] = session
                return session
            while len(self._sessions) >= self.max_sessions:
                _, expired = self._sessions.popitem(last=False)
                await expired.aclose()
            session = await factory()
            self._sessions[conversation_id] = session
            return session

    async def release(
        self, conversation_id: str, *, close: bool = False
    ) -> None:
        async with self._lock:
            session = self._sessions.pop(conversation_id, None)
        if close and session is not None:
            await session.aclose()

    async def close_all(self) -> None:
        async with self._lock:
            sessions = list(self._sessions.values())
            self._sessions.clear()
        await asyncio.gather(*(session.aclose() for session in sessions))

    def get(self, conversation_id: str) -> Optional[Any]:
        return self._sessions.get(conversation_id)
