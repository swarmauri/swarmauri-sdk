from abc import abstractmethod
from typing import Any, List, Optional, Literal
from enum import Enum, auto
from pydantic import ConfigDict, Field

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.transports.ITransport import ITransport


class TransportProtocol(Enum):
    """
    Enumeration of transportation protocols supported by the transport layer
    """

    UNICAST = auto()
    MULTICAST = auto()
    BROADCAST = auto()
    PUBSUB = auto()


@ComponentBase.register_model()
class TransportBase(ITransport, ComponentBase):
    allowed_protocols: List[TransportProtocol] = []
    resource: Optional[str] = Field(default=ResourceTypes.TRANSPORT.value, frozen=True)
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)
    type: Literal["TransportBase"] = "TransportBase"

    @abstractmethod
    def send(self, sender: str, recipient: str, message: Any) -> None:
        """
        Send a message to a specific recipient.

        Raises:
            NotImplementedError: Subclasses must implement this method.
        """
        raise NotImplementedError("send() not implemented in subclass yet.")

    @abstractmethod
    def broadcast(self, sender: str, message: Any) -> None:
        """
        Broadcast a message to all potential recipients.

        Raises:
            NotImplementedError: Subclasses must implement this method.
        """
        raise NotImplementedError("broadcast() not implemented in subclass yet.")

    @abstractmethod
    def multicast(self, sender: str, recipients: List[str], message: Any) -> None:
        """
        Send a message to multiple specific recipients.

        Raises:
            NotImplementedError: Subclasses must implement this method.
        """
        raise NotImplementedError("multicast() not implemented in subclass yet.")
