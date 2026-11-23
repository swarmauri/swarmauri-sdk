from ..transport_dependency_helpers import assert_transport_dependency_parity


def test_httpx_transport_parity_udp():
    assert_transport_dependency_parity(
        transport_package="swarmauri_transport_udp",
        parity_distribution_name="httpx",
    )
