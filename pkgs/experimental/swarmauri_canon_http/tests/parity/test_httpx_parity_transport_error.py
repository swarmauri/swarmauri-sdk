import pytest

import httpx

from swarmauri_canon_http.exceptions import HTTP2Error, HttpClientError, TimeoutError


def test_httpx_transport_error_is_httpx_exception_type():
    error = httpx.TransportError("transport failed")
    assert isinstance(error, httpx.HTTPError)


def test_canon_transport_errors_are_http_client_error_types():
    assert issubclass(TimeoutError, HttpClientError)
    assert issubclass(HTTP2Error, HttpClientError)


def test_httpx_transport_error_not_reused_by_canon_package():
    with pytest.raises(httpx.TransportError):
        raise httpx.TransportError("httpx transport")
