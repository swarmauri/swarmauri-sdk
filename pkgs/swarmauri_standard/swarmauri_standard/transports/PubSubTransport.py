from typing import Dict, Any, List, Set, Literal
import asyncio
import uuid

from pydantic import PrivateAttr
from swarmauri_base.transports.TransportBase import TransportBase
from swarmauri_base.ComponentBase import ComponentBase


@ComponentBase.register_type(TransportBase, "PubSubTransport")
class PubSubTransport(TransportBase):
    _topics: Dict[str, Set[str]] = PrivateAttr(default_factory=dict)
    _messages: Dict[str, asyncio.Queue] = PrivateAttr(default_factory=dict)
    type: Literal["PubSubTransport"] = "PubSubTransport"

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._topics = {}
        self._messages = {}

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

    def send(self, sender: str, recipient: str, message: Any) -> None:
        """Send is not supported for PubSubTransport."""
        raise NotImplementedError("send method is not supported for PubSubTransport.")
