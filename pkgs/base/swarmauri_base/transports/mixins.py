"""Pydantic mixins that pair with transport interfaces."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict

from swarmauri_core.transports.i_anycast import IAnycastTransport
from swarmauri_core.transports.i_broadcast import IBroadcastTransport
from swarmauri_core.transports.i_multicast import IMulticastTransport
from swarmauri_core.transports.i_multiplex import ChannelHandle, IMultiplexTransport
from swarmauri_core.transports.i_peer import IPeerTransport
from swarmauri_core.transports.i_unicast import IUnicastTransport


class _TransportModel(BaseModel):
    """Base class configuring Pydantic behavior for transport mixins."""

    model_config = ConfigDict(extra="allow", arbitrary_types_allowed=True)


class UnicastTransportMixin(IUnicastTransport, _TransportModel):
    """Mixin for transports implementing unicast semantics."""


class MulticastTransportMixin(IMulticastTransport, _TransportModel):
    """Mixin for transports implementing multicast semantics."""


class BroadcastTransportMixin(IBroadcastTransport, _TransportModel):
    """Mixin for transports implementing broadcast semantics."""


class AnycastTransportMixin(IAnycastTransport, _TransportModel):
    """Mixin for transports implementing anycast semantics."""


class PeerTransportMixin(IPeerTransport, _TransportModel):
    """Mixin for transports exposing peer acceptance semantics."""


class MultiplexTransportMixin(IMultiplexTransport, _TransportModel):
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
