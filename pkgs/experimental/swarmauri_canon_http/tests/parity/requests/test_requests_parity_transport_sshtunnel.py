from ..transport_dependency_helpers import assert_transport_dependency_parity


def test_requests_transport_parity_sshtunnel():
    assert_transport_dependency_parity(
        transport_package="swarmauri_transport_sshtunnel",
        parity_distribution_name="requests",
    )
