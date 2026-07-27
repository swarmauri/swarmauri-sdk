import asyncio
from contextlib import suppress

from pydantic import PrivateAttr

from swarmauri_base.live_models.LiveSessionBase import LiveSessionBase
from swarmauri_base.live_models.events.SessionErrorEvent import (
    SessionErrorEvent,
)

from .NovaSonicCodec import NovaSonicCodec


class NovaSonicLiveSession(LiveSessionBase):
    _connection = PrivateAttr()
    _codec = PrivateAttr(default_factory=NovaSonicCodec)
    _receiver = PrivateAttr(default=None)

    @classmethod
    async def create(cls, connection, setup_events):
        session = cls()
        session._connection = connection
        for event in setup_events:
            await connection.asend(event)
        session.mark_open()
        session._receiver = asyncio.create_task(session._receive_loop())
        return session

    async def _receive_loop(self) -> None:
        try:
            async for data in self._connection.aiter_events():
                for event in self._codec.decode(data):
                    await self.emit(event)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            await self.emit(SessionErrorEvent(message=str(exc)))
            await self.fail(exc)
        else:
            await self.finish()

    async def _asend_impl(self, input_data):
        await self._connection.asend(self._codec.encode(input_data))

    async def _aclose_impl(self):
        if self._receiver and self._receiver is not asyncio.current_task():
            self._receiver.cancel()
            with suppress(asyncio.CancelledError):
                await self._receiver
        await self._connection.aclose()
