from swarmauri_core.transports.enums import Feature, Protocol
from swarmauri_transport_h2 import H2Transport


def test_h2_transport_is_concrete_and_exposes_h2_capabilities() -> None:
    transport = H2Transport()

    assert not transport.__class__.__abstractmethods__
    assert Protocol.H2 in transport.supports().protocols
    assert Feature.MULTIPLEX in transport.supports().features
