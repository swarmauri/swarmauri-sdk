from swarmauri_core.transports.enums import Feature, Protocol
from swarmauri_transport_h2mux import H2MuxTransport


def test_h2_mux_is_concrete_and_advertises_real_stream_multiplexing() -> None:
    transport = H2MuxTransport()

    assert not transport.__class__.__abstractmethods__
    assert Protocol.H2 in transport.supports().protocols
    assert Feature.MULTIPLEX in transport.supports().features
