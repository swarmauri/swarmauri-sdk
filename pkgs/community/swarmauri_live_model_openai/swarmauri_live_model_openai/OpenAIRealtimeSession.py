import asyncio
import json
from contextlib import suppress
from typing import Any

from pydantic import PrivateAttr
from swarmauri_base.live_models.events.SessionErrorEvent import (
    SessionErrorEvent,
)
from swarmauri_base.live_models.LiveInputBase import LiveInputBase
from swarmauri_base.live_models.LiveSessionBase import LiveSessionBase
from swarmauri_core.transports import IWebSocketConnection

from .OpenAIRealtimeCodec import OpenAIRealtimeCodec


class OpenAIRealtimeSession(LiveSessionBase):
    _connection: IWebSocketConnection = PrivateAttr()
    _codec: OpenAIRealtimeCodec = PrivateAttr(
        default_factory=OpenAIRealtimeCodec
    )
    _receiver: Any = PrivateAttr(default=None)

    @classmethod
    async def create(
        cls, connection, setup: dict | None = None
    ) -> "OpenAIRealtimeSession":
        session = cls()
        session._connection = connection
        if setup:
            await connection.asend(json.dumps(setup))
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
            await self.emit(SessionErrorEvent(message=str(exc)))
            await self.fail(exc)
        else:
            await self.finish()

    async def _asend_impl(self, input_data: LiveInputBase) -> None:
        for message in self._codec.encode(input_data):
            await self._connection.asend(message)

    async def _aclose_impl(self) -> None:
        if (
            self._receiver is not None
            and self._receiver is not asyncio.current_task()
        ):
            self._receiver.cancel()
            with suppress(asyncio.CancelledError):
                await self._receiver
        await self._connection.aclose()
