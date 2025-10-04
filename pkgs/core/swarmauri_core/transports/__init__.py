"""Transport interfaces and shared exports for Swarmauri core."""

from .ITransport import ITransport
from .enums import AddressScheme, Cast, Feature, IOModel, Protocol, SecurityMode
from .i_anycast import IAnycastTransport
from .i_broadcast import IBroadcastTransport
from .i_multicast import IMulticastTransport
from .i_multiplex import IMultiplexTransport, ChannelHandle
from .i_peer import IPeerTransport
from .i_unicast import IUnicastTransport
from .capabilities import TransportCapabilities

__all__ = [
    "AddressScheme",
    "Cast",
    "ChannelHandle",
    "Feature",
    "IAnycastTransport",
    "IBroadcastTransport",
    "IMulticastTransport",
    "IMultiplexTransport",
    "ITransport",
    "IOModel",
    "IPeerTransport",
    "IUnicastTransport",
    "Protocol",
    "SecurityMode",
    "TransportCapabilities",
]
