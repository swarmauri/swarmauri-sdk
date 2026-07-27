from swarmauri_transport_httpx import HttpxClient


def test_httpx_client_is_concrete():
    assert not HttpxClient.__abstractmethods__


def test_resolve_url():
    client = HttpxClient(base_url="https://example.test/v1")
    assert client.resolve_url("models") == "https://example.test/v1/models"
