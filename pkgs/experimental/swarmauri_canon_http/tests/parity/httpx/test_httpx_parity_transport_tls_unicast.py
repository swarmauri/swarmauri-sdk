from ..transport_dependency_helpers import assert_transport_dependency_parity


def test_httpx_transport_parity_tls_unicast():
    assert_transport_dependency_parity(
        transport_package="swarmauri_transport_tls_unicast",
        parity_distribution_name="httpx",
    )
