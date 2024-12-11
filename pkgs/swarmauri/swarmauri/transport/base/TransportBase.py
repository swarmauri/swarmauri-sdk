from typing import Dict, Any, List
from enum import Enum, auto
import datetime
from swarmauri_core.transport.ITransport import ITransport

class TransportationProtocol(Enum):
    """
    Enumeration of transportation protocols supported by the transport layer
    """
    UNICAST = auto()
    MULTICAST = auto()
    BROADCAST = auto()
    PUBSUB = auto()

class TransportBase(ITransport):
    """
    Base class for transport transportation with shared utilities
    """
    def __init__(self, name: str):
        self.name = name
        self.subscriptions: Dict[str, List[str]] = {}
        self.message_history: List[Dict[str, Any]] = []

    def log_message(self, sender: str, recipients: List[str], message: Any, protocol: TransportationProtocol):
        """
        Log transportation events
        """
        log_entry = {
            'sender': sender,
            'recipients': recipients,
            'message': message,
            'protocol': protocol,
            'timestamp': datetime.now()
        }
        self.message_history.append(log_entry)

    def send(self, sender: str, recipient: str, message: Any) -> None:
        raise NotImplementedError("Subclasses must implement send method")

    def broadcast(self, sender: str, message: Any) -> None:
        raise NotImplementedError("Subclasses must implement broadcast method")

    def multicast(self, sender: str, recipients: List[str], message: Any) -> None:
        raise NotImplementedError("Subclasses must implement multicast method")

    def subscribe(self, topic: str, subscriber: str) -> None:
        if topic not in self.subscriptions:
            self.subscriptions[topic] = []
        if subscriber not in self.subscriptions[topic]:
            self.subscriptions[topic].append(subscriber)

    def publish(self, topic: str, message: Any) -> None:
        if topic in self.subscriptions:
            for subscriber in self.subscriptions[topic]:
                self.send(topic, subscriber, message)