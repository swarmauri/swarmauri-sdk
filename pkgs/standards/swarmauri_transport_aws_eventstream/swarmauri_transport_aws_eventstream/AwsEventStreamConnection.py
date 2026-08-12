from __future__ import annotations

from collections.abc import AsyncIterator, Iterator
from typing import Any

from pydantic import PrivateAttr
from swarmauri_base.transports.bidirectional.BidirectionalStreamConnectionBase import (  # noqa: E501
    BidirectionalStreamConnectionBase,
)
from swarmauri_base.transports.bidirectional.BidirectionalStreamState import (
    BidirectionalStreamState,
)

from .AwsEventStreamCodec import AwsEventStreamCodec


class AwsEventStreamConnection(BidirectionalStreamConnectionBase):
    """Swarmauri connection adapter for a Smithy duplex event stream."""

    _stream: Any = PrivateAttr()
    _receiver: Any = PrivateAttr(default=None)
    _codec: AwsEventStreamCodec = PrivateAttr(
        default_factory=AwsEventStreamCodec
    )

    @classmethod
    def from_stream(cls, stream: Any) -> "AwsEventStreamConnection":
        connection = cls(state=BidirectionalStreamState.OPEN.value)
        connection._stream = stream
        return connection

    async def _output_receiver(self) -> Any:
        if self._receiver is None:
            _, self._receiver = await self._stream.await_output()
        return self._receiver

    async def asend(self, event: Any) -> None:
        if self.state != BidirectionalStreamState.OPEN.value:
            raise RuntimeError("AWS event stream is not open")
        await self._stream.input_stream.send(self._codec.encode(event))

    async def areceive(self) -> Any:
        if self.state != BidirectionalStreamState.OPEN.value:
            raise EOFError("AWS event stream is closed")
        receiver = await self._output_receiver()
        event = await receiver.receive()
        if event is None:
            self.state = BidirectionalStreamState.CLOSED.value
            raise EOFError("AWS event stream ended")
        return self._codec.decode(event)

    def iter_events(self) -> Iterator[Any]:
        while self.state == BidirectionalStreamState.OPEN.value:
            try:
                yield self.receive()
            except EOFError:
                return

    async def aiter_events(self) -> AsyncIterator[Any]:
        while self.state == BidirectionalStreamState.OPEN.value:
            try:
                yield await self.areceive()
            except EOFError:
                return

    async def aclose(self) -> None:
        if self.state == BidirectionalStreamState.CLOSED.value:
            return
        self.state = BidirectionalStreamState.CLOSING.value
        await self._stream.close()
        self.state = BidirectionalStreamState.CLOSED.value
