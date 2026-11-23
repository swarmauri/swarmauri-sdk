from dataclasses import is_dataclass

from swarmauri_core.transports import (
    AddressScheme,
    Cast,
    Feature,
    IOModel,
    Protocol,
    SecurityMode,
    TransportCapabilities,
)


def test_transport_capabilities_dataclass_contract() -> None:
    """TransportCapabilities is a frozen dataclass with slots."""

    assert is_dataclass(TransportCapabilities)
    assert getattr(TransportCapabilities, "__slots__", None) is not None


def test_transport_capabilities_fields_roundtrip() -> None:
    """Creating a capability set preserves enumerated values."""

    capabilities = TransportCapabilities(
        protocols=frozenset({Protocol.UDP}),
        io=IOModel.DATAGRAM,
        casts=frozenset({Cast.UNICAST}),
        features=frozenset({Feature.RELIABLE}),
        security=SecurityMode.NONE,
        schemes=frozenset({AddressScheme.UDP}),
    )

    assert capabilities.protocols == frozenset({Protocol.UDP})
    assert capabilities.io is IOModel.DATAGRAM
    assert capabilities.casts == frozenset({Cast.UNICAST})
    assert capabilities.features == frozenset({Feature.RELIABLE})
    assert capabilities.security is SecurityMode.NONE
    assert capabilities.schemes == frozenset({AddressScheme.UDP})
