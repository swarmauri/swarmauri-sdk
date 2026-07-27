"""Pydantic mixins that pair with transport interfaces."""

from __future__ import annotations

from swarmauri_core.transports.i_anycast import IAnycastTransport
from swarmauri_core.transports.i_broadcast import IBroadcastTransport
from swarmauri_core.transports.i_multicast import IMulticastTransport
from swarmauri_core.transports.i_multiplex import (
    ChannelHandle,
    IMultiplexTransport,
)
from swarmauri_core.transports.i_peer import IPeerTransport
from swarmauri_core.transports.i_unicast import IUnicastTransport


class UnicastTransportMixin(IUnicastTransport):
    """Mixin for transports implementing unicast semantics."""


class MulticastTransportMixin(IMulticastTransport):
    """Mixin for transports implementing multicast semantics."""


class BroadcastTransportMixin(IBroadcastTransport):
    """Mixin for transports implementing broadcast semantics."""


class AnycastTransportMixin(IAnycastTransport):
    """Mixin for transports implementing anycast semantics."""


class PeerTransportMixin(IPeerTransport):
    """Mixin for transports exposing peer acceptance semantics."""


class MultiplexTransportMixin(IMultiplexTransport):
    """Mixin for transports exposing multiplexed channel semantics."""


__all__ = [
    "AnycastTransportMixin",
    "BroadcastTransportMixin",
    "MulticastTransportMixin",
    "MultiplexTransportMixin",
    "PeerTransportMixin",
    "UnicastTransportMixin",
    "ChannelHandle",
]
