from ..transport_dependency_helpers import assert_transport_dependency_parity


def test_httpx_transport_parity_uds_unicast():
    assert_transport_dependency_parity(
        transport_package="swarmauri_transport_uds_unicast",
        parity_distribution_name="httpx",
    )
