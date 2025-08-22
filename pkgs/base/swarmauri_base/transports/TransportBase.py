from abc import abstractmethod
from typing import (
    Any,
    Iterable,
    Mapping,
    Optional,
    Sequence,
    Tuple,
    TypeVar,
    Literal,
    List,
)

from pydantic import ConfigDict, Field

from swarmauri_base.ComponentBase import ComponentBase, ResourceTypes
from swarmauri_core.transports.ITransport import (
    BaseChannel,
    ClientContext,
    ITransport,
    ServerContext,
)


SC = TypeVar("SC", bound=ServerContext)
CC = TypeVar("CC", bound=ClientContext)
CH = TypeVar("CH", bound=BaseChannel)


@ComponentBase.register_model()
class TransportBase(ITransport[SC, CC, CH], ComponentBase):
    """Base component for transport implementations."""

    resource: Optional[str] = Field(default=ResourceTypes.TRANSPORT.value, frozen=True)
    model_config = ConfigDict(extra="forbid", arbitrary_types_allowed=True)
    type: Literal["TransportBase"] = "TransportBase"

    # ------------------------------------------------------------------
    # ITransport interface
    # ------------------------------------------------------------------
    @abstractmethod
    def supports(self) -> Mapping[str, Iterable[str]]:
        """Return capability metadata for discovery/diagnostics."""
        ...

    @abstractmethod
    async def make_server(
        self,
        *,
        server_cert_chain: bytes,
        server_key: bytes,
        trust_roots: Optional[bytes] = None,
        require_client_auth: bool = False,
        alpn: Optional[Sequence[str]] = None,
        ciphers: Optional[str] = None,
        min_version: Optional[Tuple[int, int]] = None,
        max_version: Optional[Tuple[int, int]] = None,
    ) -> SC: ...

    @abstractmethod
    async def make_client(
        self,
        *,
        trust_roots: bytes,
        client_cert_chain: Optional[bytes] = None,
        client_key: Optional[bytes] = None,
        alpn: Optional[Sequence[str]] = None,
        ciphers: Optional[str] = None,
        min_version: Optional[Tuple[int, int]] = None,
        max_version: Optional[Tuple[int, int]] = None,
        check_hostname: bool = True,
        server_hostname: Optional[str] = None,
    ) -> CC: ...

    @abstractmethod
    async def open_channel(
        self,
        *,
        context: SC | CC,
        target: Optional[object] = None,
    ) -> CH: ...

    @abstractmethod
    async def close_channel(self, channel: CH) -> None: ...

    @abstractmethod
    async def rehandshake(self, channel: CH) -> None: ...

    # ------------------------------------------------------------------
    # Legacy message-based API
    # ------------------------------------------------------------------
    @abstractmethod
    def send(self, sender: str, recipient: str, message: Any) -> None:
        """Send a message to a specific recipient."""
        ...

    @abstractmethod
    def broadcast(self, sender: str, message: Any) -> None:
        """Broadcast a message to all potential recipients."""
        ...

    @abstractmethod
    def multicast(self, sender: str, recipients: List[str], message: Any) -> None:
        """Send a message to multiple specific recipients."""
        ...
