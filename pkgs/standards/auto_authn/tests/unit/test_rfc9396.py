"""Tests for OAuth 2.0 Rich Authorization Requests (RFC 9396)."""

import pytest

from auto_authn.v2.routers import auth_flows


@pytest.mark.unit
@pytest.mark.xfail(reason="OAuth 2.0 RAR (RFC 9396) support is planned")
def test_authorization_request_includes_authorization_details():
    """Authorization requests can include authorization_details."""
    request_data = {
        "authorization_details": [
            {
                "type": "payment",
                "locations": ["https://api.example.com/payments"],
                "actions": ["initiate", "status"],
            }
        ]
    }

    response = auth_flows.handle_authorization_request(request_data)

    assert response["authorization_details"] == request_data["authorization_details"]


@pytest.mark.unit
@pytest.mark.xfail(reason="OAuth 2.0 RAR (RFC 9396) support is planned")
def test_token_response_includes_authorization_details():
    """Token responses echo authorization_details."""
    token_request = {
        "authorization_details": [
            {
                "type": "payment",
            }
        ]
    }

    token_response = auth_flows.issue_token(token_request)

    assert (
        token_response["authorization_details"]
        == token_request["authorization_details"]
    )
