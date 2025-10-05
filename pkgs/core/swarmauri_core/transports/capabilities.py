"""Capability definitions used by transport implementations."""

from __future__ import annotations

from dataclasses import dataclass
from typing import FrozenSet

from .enums import AddressScheme, Cast, Feature, IOModel, Protocol, SecurityMode


@dataclass(frozen=True, slots=True)
class TransportCapabilities:
    """Advertised properties for a transport implementation."""

    protocols: FrozenSet[Protocol]
    io: IOModel
    casts: FrozenSet[Cast]
    features: FrozenSet[Feature]
    security: SecurityMode
    schemes: FrozenSet[AddressScheme]
