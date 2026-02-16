from __future__ import annotations

from tigrbl.security import APIKey, HTTPBearer
from tigrbl.requests import Request


def test_http_bearer_reads_authorization_from_request_headers_attribute() -> None:
    request = Request(
        method="GET",
        path="/secure",
        headers={"Authorization": "bearer token-123"},
        query={},
        path_params={},
        body=b"",
    )

    creds = HTTPBearer()(request)

    assert creds is not None
    assert creds.credentials == "token-123"


def test_api_key_reads_query_value_from_request_query_params_attribute() -> None:
    request = Request(
        method="GET",
        path="/secure",
        headers={},
        query={"api_key": ["secret-value"]},
        path_params={},
        body=b"",
    )

    value = APIKey(name="api_key", in_="query")(request)

    assert value == "secret-value"
