from typing import Any, Dict, List, Optional, Set, Literal
import asyncio
import uuid

from pydantic import PrivateAttr
from swarmauri_base.transports.TransportBase import TransportBase
from swarmauri_base.ComponentBase import ComponentBase
from swarmauri_core.transports.capabilities import TransportCapabilities
from swarmauri_core.transports.enums import (
    AddressScheme,
    Cast,
    Feature,
    IOModel,
    Protocol,
    SecurityMode,
)


@ComponentBase.register_type(TransportBase, "PubSubTransport")
class PubSubTransport(TransportBase):
    _topics: Dict[str, Set[str]] = PrivateAttr(default_factory=dict)
    _messages: Dict[str, asyncio.Queue] = PrivateAttr(default_factory=dict)
    type: Literal["PubSubTransport"] = "PubSubTransport"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._topics = {}
        self._messages = {}

    def supports(self) -> TransportCapabilities:
        return TransportCapabilities(
            protocols=frozenset({Protocol.STDIO}),
            io=IOModel.DATAGRAM,
            casts=frozenset({Cast.BROADCAST, Cast.MULTICAST}),
            features=frozenset({Feature.RELIABLE, Feature.ORDERED, Feature.LOCAL_ONLY}),
            security=SecurityMode.NONE,
            schemes=frozenset({AddressScheme.STDIO}),
        )

    async def _start_server(self, **bind_kwargs: Any) -> None:
        return None

    async def _stop_server(self) -> None:
        return None

    async def _open_client(self, **connect_kwargs: Any) -> None:
        return None

    async def _close_client(self) -> None:
        return None

    async def subscribe(self, topic: str) -> str:
        """Subscribe to a topic and return subscriber ID."""
        subscriber_id = str(uuid.uuid4())
        if topic not in self._topics:
            self._topics[topic] = set()
        self._topics[topic].add(subscriber_id)
        self._messages[subscriber_id] = asyncio.Queue()
        return subscriber_id

    async def unsubscribe(self, topic: str, subscriber_id: str) -> None:
        """Remove subscriber from topic."""
        if topic in self._topics:
            self._topics[topic].discard(subscriber_id)
            if subscriber_id in self._messages:
                del self._messages[subscriber_id]

    async def publish(self, topic: str, message: Any) -> None:
        """Publish message to topic subscribers."""
        if topic in self._topics:
            for subscriber_id in self._topics[topic]:
                await self._messages[subscriber_id].put(message)

    async def receive(self, subscriber_id: str) -> Any:
        """Receive message for subscriber."""
        if subscriber_id in self._messages:
            return await self._messages[subscriber_id].get()
        raise ValueError(f"No queue for subscriber {subscriber_id}")

    async def broadcast(self, sender_id: str, message: Any) -> None:
        """Send message to all subscribers."""
        for topic in self._topics:
            await self.publish(topic, message)

    async def multicast(self, sender_id: str, topics: List[str], message: Any) -> None:
        """Send message to specified topics."""
        for topic in topics:
            await self.publish(topic, message)

    async def send(
        self, target: str, data: bytes, *, timeout: Optional[float] = None
    ) -> None:
        raise NotImplementedError("send is not supported for PubSubTransport.")

    async def recv(self, *, timeout: Optional[float] = None) -> bytes:
        raise NotImplementedError("recv is not supported for PubSubTransport.")
