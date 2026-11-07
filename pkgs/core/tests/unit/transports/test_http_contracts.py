from swarmauri_core.transports import (
    HttpRequestError,
    HttpStatusError,
    HttpTransportError,
    IHttpRetryPolicy,
    IManagedHttpClient,
)


def test_http_contract_exports():
    assert issubclass(HttpRequestError, HttpTransportError)
    assert issubclass(HttpStatusError, HttpTransportError)
    assert IManagedHttpClient.__abstractmethods__ >= {"close", "aclose"}
    assert IHttpRetryPolicy.__abstractmethods__ == {
        "should_retry",
        "delay_seconds",
    }
