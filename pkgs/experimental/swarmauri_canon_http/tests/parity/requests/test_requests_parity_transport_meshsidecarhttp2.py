from ..transport_dependency_helpers import assert_transport_dependency_parity


def test_requests_transport_parity_meshsidecarhttp2():
    assert_transport_dependency_parity(
        transport_package="swarmauri_transport_meshsidecarhttp2",
        parity_distribution_name="requests",
    )
