from uuid import uuid4
from typing import Dict, Any, List, Set, Literal
import asyncio
from swarmauri.transports.base.TransportBase import TransportBase


class PubSubTransport(TransportBase):

    type: Literal["PubSubTransport"] = "PubSubTransport"
    _topics: Dict[str, Set[str]] = {}  # Topic to subscriber mappings
    _subscribers: Dict[str, asyncio.Queue] = {}

    async def subscribe(self, topic: str) -> str:
        """
        Subscribe an agent to a specific topic.

        Args:
            topic (str): The topic to subscribe to

        Returns:
            str: Unique subscriber ID
        """
        subscriber_id = str(uuid4())
        self._subscribers[subscriber_id] = asyncio.Queue()

        if topic not in self._topics:
            self._topics[topic] = set()
        self._topics[topic].add(subscriber_id)

        return subscriber_id

    async def unsubscribe(self, topic: str, subscriber_id: str):
        """
        Unsubscribe an agent from a topic.

        Args:
            topic (str): The topic to unsubscribe from
            subscriber_id (str): Unique identifier of the subscriber
        """
        if topic in self._topics and subscriber_id in self._topics[topic]:
            self._topics[topic].remove(subscriber_id)
            if not self._topics[topic]:
                del self._topics[topic]

    async def publish(self, topic: str, message: Any):
        """
        Publish a message to a specific topic.

        Args:
            topic (str): The topic to publish to
            message (Any): The message to be published
        """
        if topic not in self._topics:
            return

        for subscriber_id in self._topics[topic]:
            await self._subscribers[subscriber_id].put(message)

    async def receive(self, subscriber_id: str) -> Any:
        """
        Receive messages for a specific subscriber.

        Args:
            subscriber_id (str): Unique identifier of the subscriber

        Returns:
            Any: Received message
        """
        return await self._subscribers[subscriber_id].get()

    def send(self, sender: str, recipient: str, message: Any) -> None:
        """
        Send a message to a specific recipient by creating a temporary topic.
        """
        if recipient not in self._subscribers:
            raise ValueError("Recipient not found.")
        asyncio.create_task(self._subscribers[recipient].put((sender, message)))

    def broadcast(self, sender: str, message: Any) -> None:
        """
        Broadcast a message to all subscribers of all topics.
        """
        for subscriber_queue in self._subscribers.values():
            asyncio.create_task(subscriber_queue.put((sender, message)))

    def multicast(self, sender: str, recipients: List[str], message: Any) -> None:
        """
        Send a message to multiple specific recipients.
        """
        for recipient in recipients:
            if recipient in self._subscribers:
                asyncio.create_task(self._subscribers[recipient].put((sender, message)))
