from __future__ import annotations

from abc import ABC, abstractmethod
from typing import (
    Generic,
    Iterable,
    Mapping,
    Optional,
    Protocol,
    Sequence,
    Tuple,
    TypeVar,
    runtime_checkable,
)

__all__ = [
    "Version",
    "BaseChannel",
    "ByteStream",
    "Multiplex",
    "ServerContext",
    "ClientContext",
    "ITransport",
]


# ---------------------------------------------------------------------------
# Common version tuple (e.g., (1, 3) for TLS 1.3)
# ---------------------------------------------------------------------------
Version = Tuple[int, int]


# ---------------------------------------------------------------------------
# Channel Protocols (shared minimal semantics across transports)
# ---------------------------------------------------------------------------
@runtime_checkable
class BaseChannel(Protocol):
    """
    Minimal lifecycle shared by all secure transports (TLS, QUIC, SSH, …).
    Concrete channels MAY add richer, backend-specific APIs.
    """

    async def close(self) -> None: ...

    @property
    def is_open(self) -> bool: ...


@runtime_checkable
class ByteStream(Protocol):
    """
    Byte stream semantics for request/response or streaming data.
    Examples:
      • TLS-over-TCP stream
      • QUIC bidirectional stream
      • SSH channel carrying a TCP-like stream
    """

    async def send(self, data: bytes) -> int: ...

    async def recv(self, n: int = 65536) -> bytes: ...


@runtime_checkable
class Multiplex(Protocol):
    """
    Multiplexing capability (multiple logical streams on one secure connection).
    Examples:
      • HTTP/2 over TLS
      • HTTP/3 over QUIC
      • SSH multiple channels
    """

    async def open_stream(self) -> ByteStream: ...

    async def close_stream(self, stream: ByteStream) -> None: ...

    @property
    def stream_count(self) -> int: ...


# ---------------------------------------------------------------------------
# Context Protocols (opaque handles for configuration / credentials)
# ---------------------------------------------------------------------------
@runtime_checkable
class ServerContext(Protocol):
    """
    Opaque server-side transport context (e.g., ssl.SSLContext, quic.Configuration).
    Marker protocol — concrete backends expose their own methods.
    """

    ...  # no required members


@runtime_checkable
class ClientContext(Protocol):
    """
    Opaque client-side transport context.
    Marker protocol — concrete backends expose their own methods.
    """

    ...  # no required members


# ---------------------------------------------------------------------------
# Type Parameters
#   SC = concrete ServerContext type
#   CC = concrete ClientContext type
#   CH = concrete Channel type (implements BaseChannel; may also implement
#        ByteStream and/or Multiplex)
# ---------------------------------------------------------------------------
SC = TypeVar("SC", bound=ServerContext)
CC = TypeVar("CC", bound=ClientContext)
CH = TypeVar("CH", bound=BaseChannel)


# ---------------------------------------------------------------------------
# ITransport (Abstract Base Class)
#   • Build server/client secure contexts (TLS/mTLS, QUIC, SSH, …)
#   • Open/close a secure channel bound to a context
#   • Re-handshake/refresh channel (for key/cert rotation, 0-RTT upgrades, etc.)
#   • Strictly transport-layer; no data-crypto (AEAD/MRE) or key lifecycle here
# ---------------------------------------------------------------------------
class ITransport(Generic[SC, CC, CH], ABC):
    """
    Abstract base for secure transport providers.

    Design notes
    ------------
    • Strongly-typed via generics:
        SC = server-context type (implements ServerContext)
        CC = client-context type (implements ClientContext)
        CH = channel type (implements BaseChannel; may also satisfy ByteStream/Multiplex)
    • The 'context' objects are created once and reused by the runtime (servers/clients).
    • The 'channel' represents an established secure connection/session.
    """

    # ------------- Capabilities / metadata -------------
    @abstractmethod
    def supports(self) -> Mapping[str, Iterable[str]]:
        """
        Return capability metadata (string lists only) for discovery/diagnostics.

        Example result:
            {
              "protocols": ("TLS1.3", "QUIC", "SSH"),
              "features": ("mtls", "alpn", "multiplex", "0rtt"),
              "alpn": ("h2", "http/1.1", "h3"),
            }
        """

    # ------------- Server context factory -------------
    @abstractmethod
    async def make_server(
        self,
        *,
        server_cert_chain: bytes,  # PEM (leaf + intermediates)
        server_key: bytes,  # PEM PKCS#8 (or backend-accepted encoding)
        trust_roots: Optional[bytes] = None,  # PEM bundle for client auth (mTLS)
        require_client_auth: bool = False,
        alpn: Optional[Sequence[str]] = None,
        ciphers: Optional[str] = None,
        min_version: Optional[Version] = None,
        max_version: Optional[Version] = None,
    ) -> SC:
        """
        Create a secure server context.

        Returns
        -------
        SC
            A concrete server context handle usable by the server runtime
            (e.g., ASGI server, QUIC listener, SSH daemon).
        """

    # ------------- Client context factory -------------
    @abstractmethod
    async def make_client(
        self,
        *,
        trust_roots: bytes,  # PEM bundle to validate server
        client_cert_chain: Optional[bytes] = None,  # PEM for mTLS (optional)
        client_key: Optional[bytes] = None,  # PEM PKCS#8 for mTLS (optional)
        alpn: Optional[Sequence[str]] = None,
        ciphers: Optional[str] = None,
        min_version: Optional[Version] = None,
        max_version: Optional[Version] = None,
        check_hostname: bool = True,
        server_hostname: Optional[
            str
        ] = None,  # required by some backends when check_hostname=True
    ) -> CC:
        """
        Create a secure client context.

        Returns
        -------
        CC
            A concrete client context handle usable by HTTP/WS/QUIC/SSH clients.
        """

    # ------------- Channel / session lifecycle -------------
    @abstractmethod
    async def open_channel(
        self,
        *,
        context: SC | CC,
        target: Optional[object] = None,
    ) -> CH:
        """
        Open an established secure channel using a server or client context.

        Notes
        -----
        • TLS: 'target' may be a connected TCP socket to be wrapped.
        • QUIC: 'target' may be a (host, port) tuple to connect.
        • SSH:  'target' may be connection parameters or a socket.

        Returns
        -------
        CH
            A concrete channel object. It MUST implement BaseChannel and MAY
            also implement ByteStream and/or Multiplex.
        """

    @abstractmethod
    async def close_channel(self, channel: CH) -> None:
        """Close a previously opened secure channel."""

    @abstractmethod
    async def rehandshake(self, channel: CH) -> None:
        """
        Re-negotiate transport parameters/keys on the channel.

        Examples
        --------
        • Trigger TLS key update / renegotiation (where supported).
        • Refresh QUIC keys or validate post-rotation certs.
        """
