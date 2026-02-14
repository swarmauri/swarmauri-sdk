import pytest

import httpx

from swarmauri_canon_http import HttpClient


def test_httpx_async_base_transport_is_available():
    assert hasattr(httpx, "AsyncBaseTransport")
    assert issubclass(httpx.AsyncBaseTransport, object)


def test_canon_client_rejects_async_transport_keyword():
    with pytest.raises(TypeError):
        HttpClient(base_url="http://example.com", transport=httpx.AsyncBaseTransport())
