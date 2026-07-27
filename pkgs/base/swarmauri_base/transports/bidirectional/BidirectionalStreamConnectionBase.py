"""Shared lifecycle for bidirectional streams."""

import asyncio
from abc import abstractmethod
from collections.abc import AsyncIterator, Iterator
from typing import Any
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

from swarmauri_core.transports.i_bidirectional_stream import (
    IBidirectionalStreamConnection,
)

from .BidirectionalStreamState import BidirectionalStreamState


class BidirectionalStreamConnectionBase(
    IBidirectionalStreamConnection, BaseModel
):
    connection_id: str = Field(default_factory=lambda: str(uuid4()))
    state: str = BidirectionalStreamState.NEW.value
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="allow")

    @staticmethod
    def _run_sync(awaitable: Any) -> Any:
        try:
            asyncio.get_running_loop()
        except RuntimeError:
            return asyncio.run(awaitable)
        raise RuntimeError("Use the async stream API inside an event loop")

    def send(self, event: Any) -> None:
        self._run_sync(self.asend(event))

    @abstractmethod
    async def asend(self, event: Any) -> None: ...

    def receive(self) -> Any:
        return self._run_sync(self.areceive())

    @abstractmethod
    async def areceive(self) -> Any: ...

    def iter_events(self) -> Iterator[Any]:
        while self.state == BidirectionalStreamState.OPEN.value:
            yield self.receive()

    async def aiter_events(self) -> AsyncIterator[Any]:
        while self.state == BidirectionalStreamState.OPEN.value:
            yield await self.areceive()

    def close(self) -> None:
        self._run_sync(self.aclose())

    @abstractmethod
    async def aclose(self) -> None: ...
