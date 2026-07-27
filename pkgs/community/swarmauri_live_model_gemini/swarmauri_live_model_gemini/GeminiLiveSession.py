import asyncio
from contextlib import suppress
from typing import Any

from pydantic import PrivateAttr

from swarmauri_base.live_models import LiveInputBase, LiveSessionBase
from swarmauri_core.transports import IWebSocketConnection

from .GeminiLiveCodec import GeminiLiveCodec


class GeminiLiveSession(LiveSessionBase):
    _connection: IWebSocketConnection = PrivateAttr()
    _codec: GeminiLiveCodec = PrivateAttr(default_factory=GeminiLiveCodec)
    _receiver: Any = PrivateAttr(default=None)

    @classmethod
    async def create(
        cls, connection: IWebSocketConnection, setup: dict
    ) -> "GeminiLiveSession":
        session = cls()
        session._connection = connection
        await connection.asend(__import__("json").dumps(setup))
        session.mark_open()
        session._receiver = asyncio.create_task(session._receive_loop())
        return session

    async def _receive_loop(self) -> None:
        try:
            async for message in self._connection.aiter_messages():
                for event in self._codec.decode(message):
                    await self.emit(event)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            from swarmauri_base.live_models.events import SessionErrorEvent

            await self.emit(SessionErrorEvent(message=str(exc)))

    async def _asend_impl(self, input_data: LiveInputBase) -> None:
        await self._connection.asend(self._codec.encode(input_data))

    async def _aclose_impl(self) -> None:
        if self._receiver is not None:
            self._receiver.cancel()
            with suppress(asyncio.CancelledError):
                await self._receiver
        await self._connection.aclose()
