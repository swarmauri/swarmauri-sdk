from __future__ import annotations

from abc import abstractmethod
from enum import Enum, auto
from typing import Any, List, Optional, Literal

from pydantic import ConfigDict, Field, PrivateAttr

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.transports import ITransport


class TransportProtocol(Enum):
    """
    Enumeration of transportation protocols supported by the transport layer
    """

    UNICAST = auto()
    MULTICAST = auto()
    BROADCAST = auto()
    PUBSUB = auto()


@ComponentBase.register_model()
class TransportBase(ITransport[Any, Any], ComponentBase):
    """Base implementation of :class:`ITransport`."""

    allowed_protocols: List[TransportProtocol] = []
    resource: Optional[str] = Field(default=ResourceTypes.TRANSPORT.value, frozen=True)
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)
    type: Literal["TransportBase"] = "TransportBase"

    _connected: bool = PrivateAttr(default=False)

    async def connect(self, **opts: Any) -> None:
        """Mark the transport as connected."""
        self._connected = True

    async def close(self) -> None:
        """Mark the transport as closed."""
        self._connected = False

    def is_connected(self) -> bool:
        return self._connected

    @abstractmethod
    async def send(self, msg: Any, **meta: Any) -> None:
        """Send a single message."""

    @abstractmethod
    async def recv(self, **opts: Any) -> Any:
        """Receive a single message."""
