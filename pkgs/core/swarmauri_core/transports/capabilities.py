"""Capability definitions used by transport implementations."""

from __future__ import annotations

from dataclasses import dataclass

from .enums import (
    AddressScheme,
    Cast,
    Feature,
    IOModel,
    Protocol,
    SecurityMode,
)


@dataclass(frozen=True, slots=True)
class TransportCapabilities:
    """Advertised properties for a transport implementation."""

    protocols: frozenset[Protocol]
    io: IOModel
    casts: frozenset[Cast]
    features: frozenset[Feature]
    security: SecurityMode
    schemes: frozenset[AddressScheme]
