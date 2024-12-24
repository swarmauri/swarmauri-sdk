from typing import Dict, Any, List, Optional, Set, Literal
from uuid import uuid4
import asyncio
from swarmauri_base.transports.TransportBase import TransportBase


class PubSubTransport(TransportBase):
    allowed_protocols: List[TransportProtocol] = [TransportProtocol.PUBSUB]
    _topics: Dict[str, Set[str]] = {}  # Topic to subscriber mappings
    _subscribers: Dict[str, asyncio.Queue] = {}
    type: Literal["PubSubTransport"] = "PubSubTransport"

    async def subscribe(self, topic: str) -> str:
        """
        Subscribe an agent to a specific topic.

        Args:
            topic (str): The topic to subscribe to

        Returns:
            str: Unique subscriber ID
        """
        subscriber_id = self.id

        # Create message queue for this subscribere
        self._subscribers[subscriber_id] = asyncio.Queue()

        # Add subscriber to topic
        if topic not in self._topics:
            self._topics[topic] = set()
        self._topics[topic].add(subscriber_id)

        return subscriber_id

    async def unsubscribe(self, topic: str):
        """
        Unsubscribe an agent from a topic.

        Args:
            topic (str): The topic to unsubscribe from
            subscriber_id (str): Unique identifier of the subscriber
        """
        subscriber_id = self.id
        if topic in self._topics and subscriber_id in self._topics[topic]:
            self._topics[topic].remove(subscriber_id)

            # Optional: Clean up if no subscribers remain
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

        # Distribute message to all subscribers of this topic
        for subscriber_id in self._topics[topic]:
            await self._subscribers[subscriber_id].put(message)

    async def receive(self) -> Any:
        """
        Receive messages for a specific subscriber.

        Args:
            subscriber_id (str): Unique identifier of the subscriber

        Returns:
            Any: Received message
        """
        return await self._subscribers[self.id].get()

    def send(self, sender: str, recipient: str, message: Any) -> None:
        """
        Simulate sending a direct message (not applicable in Pub/Sub context).

        Args:
            sender (str): The sender ID
            recipient (str): The recipient ID
            message (Any): The message to send

        Raises:
            NotImplementedError: This method is not applicable for Pub/Sub.
        """
        raise NotImplementedError("Direct send not supported in Pub/Sub model.")

    def broadcast(self, sender: str, message: Any) -> None:
        """
        Broadcast a message to all subscribers of all topics.

        Args:
            sender (str): The sender ID
            message (Any): The message to broadcast
        """
        for topic in self._topics:
            asyncio.create_task(self.publish(topic, message))

    def multicast(self, sender: str, recipients: List[str], message: Any) -> None:
        """
        Send a message to specific topics (acting as recipients).

        Args:
            sender (str): The sender ID
            recipients (List[str]): Topics to send the message to
            message (Any): The message to send
        """
        for topic in recipients:
            asyncio.create_task(self.publish(topic, message))


check = PubSubTransport()
print(check.type)
print("I am okay")
