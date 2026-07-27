"""Pydantic mixins that pair with transport interfaces."""

from __future__ import annotations

from pydantic import BaseModel
from swarmauri_core.transports.i_anycast import IAnycastTransport
from swarmauri_core.transports.i_broadcast import IBroadcastTransport
from swarmauri_core.transports.i_multicast import IMulticastTransport
from swarmauri_core.transports.i_multiplex import (
    ChannelHandle,
    IMultiplexTransport,
)
from swarmauri_core.transports.i_peer import IPeerTransport
from swarmauri_core.transports.i_unicast import IUnicastTransport


class UnicastTransportMixin(IUnicastTransport, BaseModel):
    """Mixin for transports implementing unicast semantics."""


class MulticastTransportMixin(IMulticastTransport, BaseModel):
    """Mixin for transports implementing multicast semantics."""


class BroadcastTransportMixin(IBroadcastTransport, BaseModel):
    """Mixin for transports implementing broadcast semantics."""


class AnycastTransportMixin(IAnycastTransport, BaseModel):
    """Mixin for transports implementing anycast semantics."""


class PeerTransportMixin(IPeerTransport, BaseModel):
    """Mixin for transports exposing peer acceptance semantics."""


class MultiplexTransportMixin(IMultiplexTransport, BaseModel):
    """Mixin for transports exposing multiplexed channel semantics."""


__all__ = [
    "AnycastTransportMixin",
    "BroadcastTransportMixin",
    "ChannelHandle",
    "MulticastTransportMixin",
    "MultiplexTransportMixin",
    "PeerTransportMixin",
    "UnicastTransportMixin",
]
