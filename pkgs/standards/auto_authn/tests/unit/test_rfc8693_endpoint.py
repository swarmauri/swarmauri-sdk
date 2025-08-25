"""Tests for RFC 8693 OAuth 2.0 Token Exchange endpoint.
See RFC 8693: https://www.rfc-editor.org/rfc/rfc8693
"""

from unittest.mock import MagicMock, patch

from auto_authn.v2.rfc8693 import (
    RFC8693_SPEC_URL,
    TOKEN_EXCHANGE_GRANT_TYPE,
    TokenType,
)
from auto_authn.v2.rfc7519 import encode_jwt


def test_token_exchange_endpoint_enabled(test_client, enable_rfc8693):
    """RFC 8693: enabled token exchange returns a new token."""
    subject_jwt = encode_jwt(sub="user123")
    with patch("auto_authn.v2.rfc8693.JWTCoder") as mock_jwt:
        mock_instance = MagicMock()
        mock_jwt.default.return_value = mock_instance
        mock_instance.sign.return_value = "exchanged-token"

        response = test_client.post(
            "/token/exchange",
            data={
                "grant_type": TOKEN_EXCHANGE_GRANT_TYPE,
                "subject_token": subject_jwt,
                "subject_token_type": TokenType.JWT.value,
            },
        )

    assert response.status_code == 200
    assert response.json()["access_token"] == "exchanged-token"


def test_token_exchange_endpoint_disabled(test_client):
    """RFC 8693: disabled token exchange is unavailable."""
    subject_jwt = encode_jwt(sub="user123")
    response = test_client.post(
        "/token/exchange",
        data={
            "grant_type": TOKEN_EXCHANGE_GRANT_TYPE,
            "subject_token": subject_jwt,
            "subject_token_type": TokenType.JWT.value,
        },
    )

    assert response.status_code == 404


def test_rfc8693_spec_url():
    """RFC 8693: Spec URL reference."""
    assert RFC8693_SPEC_URL.endswith("/rfc8693")
