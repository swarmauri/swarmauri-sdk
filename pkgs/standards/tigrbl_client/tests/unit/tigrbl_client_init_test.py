import pytest
import httpx
from tigrbl_client import TigrblClient


@pytest.mark.unit
def test_init_sets_properties():
    client = TigrblClient("https://example.com")
    assert client._endpoint == "https://example.com"
    assert client._own is True
    assert isinstance(client._client, httpx.Client)


@pytest.mark.unit
def test_init_uses_provided_client():
    mock_client = httpx.Client()
    try:
        client = TigrblClient("https://example.com", client=mock_client)
        assert client._client is mock_client
        assert client._own is False
    finally:
        mock_client.close()
