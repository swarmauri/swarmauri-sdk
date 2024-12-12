from typing import Dict, Any, List, Optional, Literal
from enum import Enum, auto
from swarmauri_core.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.transport.ITransport import ITransport


class TransportationProtocol(Enum):
    """
    Enumeration of transportation protocols supported by the transport layer
    """

    UNICAST = auto()
    MULTICAST = auto()
    BROADCAST = auto()
    PUBSUB = auto()


class TransportBase(ITransport, ComponentBase):
    allowed_protocols: List[TransportationProtocol] = []
    resource: Optional[str] = ResourceTypes.TRANSPORT.value
    type: Literal["TransportBase"] = "TransportBase"

    def send(self, sender: str, recipient: str, message: Any) -> None:
        """
        Send a message to a specific recipient.

        Raises:
            NotImplementedError: Subclasses must implement this method.
        """
        raise NotImplementedError("send() not implemented in subclass yet.")

    def broadcast(self, sender: str, message: Any) -> None:
        """
        Broadcast a message to all potential recipients.

        Raises:
            NotImplementedError: Subclasses must implement this method.
        """
        raise NotImplementedError("broadcast() not implemented in subclass yet.")

    def multicast(self, sender: str, recipients: List[str], message: Any) -> None:
        """
        Send a message to multiple specific recipients.

        Raises:
            NotImplementedError: Subclasses must implement this method.
        """
        raise NotImplementedError("multicast() not implemented in subclass yet.")
