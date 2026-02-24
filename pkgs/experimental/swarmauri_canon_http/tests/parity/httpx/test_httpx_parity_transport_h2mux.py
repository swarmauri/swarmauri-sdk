from ..transport_dependency_helpers import assert_transport_dependency_parity


def test_httpx_transport_parity_h2mux():
    assert_transport_dependency_parity(
        transport_package="swarmauri_transport_h2mux",
        parity_distribution_name="httpx",
    )
