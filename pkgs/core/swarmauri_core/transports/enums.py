"""Enumerations describing transport capabilities and behaviors."""

from __future__ import annotations

from enum import Enum, auto


class Protocol(Enum):
    """Network or IPC protocol used by a transport implementation."""

    TCP = auto()
    UDP = auto()
    UDS = auto()
    TLS = auto()
    QUIC = auto()


class IOModel(Enum):
    """I/O semantics that a transport uses for communication."""

    STREAM = auto()
    DATAGRAM = auto()


class Cast(Enum):
    """Message distribution styles supported by a transport."""

    UNICAST = auto()
    MULTICAST = auto()
    BROADCAST = auto()
    ANYCAST = auto()


class Feature(Enum):
    """Optional features that a transport can provide."""

    RELIABLE = auto()
    ORDERED = auto()
    ENCRYPTED = auto()
    AUTHENTICATED = auto()
    MUTUAL_AUTH = auto()
    LOCAL_ONLY = auto()
    MULTIPLEX = auto()


class SecurityMode(Enum):
    """Security posture of a transport implementation."""

    NONE = auto()
    TLS = auto()
    MTLS = auto()


class AddressScheme(Enum):
    """Addressing schemes a transport understands."""

    TCP = auto()
    UDP = auto()
    UDS = auto()
    TLS = auto()
    QUIC = auto()
