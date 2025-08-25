"""Tests for RFC 8693: OAuth 2.0 Token Exchange.

See RFC 8693: https://www.rfc-editor.org/rfc/rfc8693
"""

from unittest.mock import patch

import pytest
from fastapi import FastAPI

from auto_authn.v2.rfc8693 import (
    RFC8693_SPEC_URL,
    TokenType,
    TokenExchangeRequest,
    TokenExchangeResponse,
    validate_token_exchange_request,
    validate_subject_token,
    exchange_token,
    create_impersonation_token,
    create_delegation_token,
    TOKEN_EXCHANGE_GRANT_TYPE,
    include_rfc8693,
)
from auto_authn.v2.runtime_cfg import settings
from auto_authn.v2.rfc7519 import encode_jwt
import time

pytestmark = pytest.mark.usefixtures("enable_rfc8693")


@pytest.mark.unit
def test_token_exchange_request_valid():
    """RFC 8693: Valid token exchange request creation."""
    request = TokenExchangeRequest(
        grant_type=TOKEN_EXCHANGE_GRANT_TYPE,
        subject_token="subject-token-123",
        subject_token_type=TokenType.ACCESS_TOKEN.value,
        actor_token="actor-token-456",
        actor_token_type=TokenType.ACCESS_TOKEN.value,
        audience="https://api.example.com",
        scope="read write",
    )

    assert request.grant_type == TOKEN_EXCHANGE_GRANT_TYPE
    assert request.subject_token == "subject-token-123"
    assert request.actor_token == "actor-token-456"
    assert request.audience == "https://api.example.com"
    assert request.scope == "read write"


@pytest.mark.unit
def test_token_exchange_request_validation_success():
    """RFC 8693: Valid request should pass validation."""
    request = TokenExchangeRequest(
        grant_type=TOKEN_EXCHANGE_GRANT_TYPE,
        subject_token="subject-token-123",
        subject_token_type=TokenType.ACCESS_TOKEN.value,
    )

    # Should not raise
    request.validate()


@pytest.mark.unit
def test_token_exchange_request_validation_invalid_grant_type():
    """RFC 8693: Invalid grant_type should raise ValueError."""
    request = TokenExchangeRequest(
        grant_type="invalid-grant-type",
        subject_token="subject-token-123",
        subject_token_type=TokenType.ACCESS_TOKEN.value,
    )

    with pytest.raises(ValueError, match="Invalid grant_type"):
        request.validate()


@pytest.mark.unit
def test_token_exchange_request_validation_missing_subject_token():
    """RFC 8693: Missing subject_token should raise ValueError."""
    request = TokenExchangeRequest(
        grant_type=TOKEN_EXCHANGE_GRANT_TYPE,
        subject_token="",
        subject_token_type=TokenType.ACCESS_TOKEN.value,
    )

    with pytest.raises(ValueError, match="subject_token is required"):
        request.validate()


@pytest.mark.unit
def test_token_exchange_request_validation_actor_token_without_type():
    """RFC 8693: Actor token without type should raise ValueError."""
    request = TokenExchangeRequest(
        grant_type=TOKEN_EXCHANGE_GRANT_TYPE,
        subject_token="subject-token-123",
        subject_token_type=TokenType.ACCESS_TOKEN.value,
        actor_token="actor-token-456",
        # Missing actor_token_type
    )

    with pytest.raises(ValueError, match="actor_token_type is required"):
        request.validate()


@pytest.mark.unit
def test_token_exchange_response_to_dict():
    """RFC 8693: Token exchange response serialization."""
    response = TokenExchangeResponse(
        access_token="new-access-token",
        token_type="Bearer",
        expires_in=3600,
        refresh_token="new-refresh-token",
        scope="read",
        issued_token_type=TokenType.ACCESS_TOKEN.value,
    )

    result = response.to_dict()

    assert result["access_token"] == "new-access-token"
    assert result["token_type"] == "Bearer"
    assert result["expires_in"] == 3600
    assert result["refresh_token"] == "new-refresh-token"
    assert result["scope"] == "read"
    assert result["issued_token_type"] == TokenType.ACCESS_TOKEN.value


@pytest.mark.unit
def test_token_exchange_response_minimal():
    """RFC 8693: Minimal token exchange response."""
    response = TokenExchangeResponse(
        access_token="new-access-token",
    )

    result = response.to_dict()

    assert result["access_token"] == "new-access-token"
    assert result["token_type"] == "Bearer"
    assert "expires_in" not in result
    assert "refresh_token" not in result


@pytest.mark.unit
def test_validate_token_exchange_request():
    """RFC 8693: Validate token exchange request with settings check."""
    with patch.object(settings, "enable_rfc8693", True):
        request = validate_token_exchange_request(
            grant_type=TOKEN_EXCHANGE_GRANT_TYPE,
            subject_token="subject-token-123",
            subject_token_type=TokenType.ACCESS_TOKEN.value,
            audience="https://api.example.com",
        )

        assert isinstance(request, TokenExchangeRequest)
        assert request.audience == "https://api.example.com"


@pytest.mark.unit
def test_validate_token_exchange_request_disabled():
    """RFC 8693: Request validation when disabled should raise RuntimeError."""
    with patch.object(settings, "enable_rfc8693", False):
        with pytest.raises(RuntimeError, match="RFC 8693 support disabled"):
            validate_token_exchange_request(
                grant_type=TOKEN_EXCHANGE_GRANT_TYPE,
                subject_token="subject-token-123",
                subject_token_type=TokenType.ACCESS_TOKEN.value,
            )


@pytest.mark.unit
def test_validate_subject_token_jwt():
    """RFC 8693: Validate JWT subject token."""
    # Create a valid JWT
    jwt_token = encode_jwt(
        sub="user123",
        tid="tenant-1",
        iss="https://auth.example.com",
        aud="https://api.example.com",
        exp=int(time.time()) + 3600,
        iat=int(time.time()),
    )

    claims = validate_subject_token(jwt_token, TokenType.JWT.value)

    assert claims["sub"] == "user123"
    assert claims["iss"] == "https://auth.example.com"


@pytest.mark.unit
def test_validate_subject_token_access_token():
    """RFC 8693: Validate access token (JWT format)."""
    jwt_token = encode_jwt(
        sub="user123",
        tid="tenant-1",
        scope="read write",
        exp=int(time.time()) + 3600,
    )

    claims = validate_subject_token(jwt_token, TokenType.ACCESS_TOKEN.value)

    assert claims["sub"] == "user123"
    assert claims["scope"] == "read write"


@pytest.mark.unit
def test_validate_subject_token_refresh_token():
    """RFC 8693: Validate refresh token (opaque)."""
    refresh_token = "refresh-token-abc-123"

    result = validate_subject_token(refresh_token, TokenType.REFRESH_TOKEN.value)

    assert result["token_type"] == "refresh_token"
    assert result["value"] == refresh_token


@pytest.mark.unit
def test_validate_subject_token_invalid_jwt():
    """RFC 8693: Invalid JWT should raise ValueError."""
    invalid_jwt = "invalid.jwt.token"

    with pytest.raises(ValueError, match="Invalid JWT token"):
        validate_subject_token(invalid_jwt, TokenType.JWT.value)


@pytest.mark.unit
def test_validate_subject_token_empty():
    """RFC 8693: Empty token should raise ValueError."""
    with pytest.raises(ValueError, match="Empty token"):
        validate_subject_token("", TokenType.SAML1.value)


@pytest.mark.unit
def test_exchange_token():
    """RFC 8693: Perform token exchange."""
    # Create subject token
    subject_jwt = encode_jwt(
        sub="user123",
        tid="tenant-1",
        scope="read write",
        exp=int(time.time()) + 3600,
    )

    request = TokenExchangeRequest(
        grant_type=TOKEN_EXCHANGE_GRANT_TYPE,
        subject_token=subject_jwt,
        subject_token_type=TokenType.ACCESS_TOKEN.value,
        audience="https://api.example.com",
        scope="read",  # Narrower scope
    )

    with patch("auto_authn.v2.rfc8693.encode_jwt") as mock_encode_jwt:
        mock_encode_jwt.return_value = "new-access-token-xyz"

        response = exchange_token(request, issuer="https://token-exchange.example.com")

        assert response.access_token == "new-access-token-xyz"
        assert response.token_type == "Bearer"
        assert response.scope == "read"
        assert response.expires_in == 3600

        # Verify JWT helper was called correctly
        mock_encode_jwt.assert_called_once()
        call_args = mock_encode_jwt.call_args[1]
        assert call_args["sub"] == "user123"
        assert call_args["tid"] == "tenant-1"
        assert call_args["scopes"] == ["read"]


@pytest.mark.unit
def test_exchange_token_with_actor():
    """RFC 8693: Token exchange with actor token."""
    subject_jwt = encode_jwt(sub="user123", tid="tenant-1", exp=int(time.time()) + 3600)
    actor_jwt = encode_jwt(sub="admin456", tid="tenant-1", exp=int(time.time()) + 3600)

    request = TokenExchangeRequest(
        grant_type=TOKEN_EXCHANGE_GRANT_TYPE,
        subject_token=subject_jwt,
        subject_token_type=TokenType.ACCESS_TOKEN.value,
        actor_token=actor_jwt,
        actor_token_type=TokenType.ACCESS_TOKEN.value,
    )

    with patch("auto_authn.v2.rfc8693.encode_jwt") as mock_encode_jwt:
        mock_encode_jwt.return_value = "impersonation-token"

        response = exchange_token(request, issuer="https://auth.example.com")

        assert response.access_token == "impersonation-token"


@pytest.mark.unit
def test_create_impersonation_token():
    """RFC 8693: Create impersonation token."""
    subject_jwt = encode_jwt(sub="user123", tid="tenant-1", exp=int(time.time()) + 3600)
    actor_jwt = encode_jwt(sub="admin456", tid="tenant-1", exp=int(time.time()) + 3600)

    with patch("auto_authn.v2.rfc8693.exchange_token") as mock_exchange:
        mock_response = TokenExchangeResponse(access_token="impersonation-token")
        mock_exchange.return_value = mock_response

        response = create_impersonation_token(
            subject_token=subject_jwt,
            actor_token=actor_jwt,
            audience="https://api.example.com",
            scope="read",
        )

        assert response.access_token == "impersonation-token"

        # Verify exchange_token was called with correct parameters
        mock_exchange.assert_called_once()
        call_args = mock_exchange.call_args[0][0]  # First positional arg (request)
        assert call_args.subject_token == subject_jwt
        assert call_args.actor_token == actor_jwt
        assert call_args.audience == "https://api.example.com"
        assert call_args.scope == "read"


@pytest.mark.unit
def test_create_delegation_token():
    """RFC 8693: Create delegation token."""
    subject_jwt = encode_jwt(
        sub="user123",
        tid="tenant-1",
        scope="read write admin",
        exp=int(time.time()) + 3600,
    )

    with patch("auto_authn.v2.rfc8693.exchange_token") as mock_exchange:
        mock_response = TokenExchangeResponse(
            access_token="delegation-token", scope="read"
        )
        mock_exchange.return_value = mock_response

        response = create_delegation_token(
            subject_token=subject_jwt,
            audience="https://api.example.com",
            scope="read",  # Narrower scope for delegation
        )

        assert response.access_token == "delegation-token"
        assert response.scope == "read"

        # Verify no actor token was used
        call_args = mock_exchange.call_args[0][0]
        assert call_args.actor_token is None
        assert call_args.scope == "read"


@pytest.mark.unit
def test_exchange_token_disabled():
    """RFC 8693: exchange_token should honor feature flag."""
    subject_jwt = encode_jwt(sub="user123", tid="tenant-1", exp=int(time.time()) + 3600)
    request = TokenExchangeRequest(
        grant_type=TOKEN_EXCHANGE_GRANT_TYPE,
        subject_token=subject_jwt,
        subject_token_type=TokenType.ACCESS_TOKEN.value,
    )

    with patch.object(settings, "enable_rfc8693", False):
        with pytest.raises(RuntimeError, match="RFC 8693 support disabled"):
            exchange_token(request, issuer="https://auth.example.com")


@pytest.mark.unit
def test_create_impersonation_token_disabled():
    """RFC 8693: create_impersonation_token should honor feature flag."""
    subject_jwt = encode_jwt(sub="user123", tid="tenant-1", exp=int(time.time()) + 3600)
    actor_jwt = encode_jwt(sub="admin456", tid="tenant-1", exp=int(time.time()) + 3600)

    with patch.object(settings, "enable_rfc8693", False):
        with pytest.raises(RuntimeError, match="RFC 8693 support disabled"):
            create_impersonation_token(
                subject_token=subject_jwt,
                actor_token=actor_jwt,
            )


@pytest.mark.unit
def test_create_delegation_token_disabled():
    """RFC 8693: create_delegation_token should honor feature flag."""
    subject_jwt = encode_jwt(sub="user123", tid="tenant-1", exp=int(time.time()) + 3600)

    with patch.object(settings, "enable_rfc8693", False):
        with pytest.raises(RuntimeError, match="RFC 8693 support disabled"):
            create_delegation_token(subject_token=subject_jwt)


@pytest.mark.unit
def test_token_type_enum():
    """RFC 8693: Token type enum values."""
    assert (
        TokenType.ACCESS_TOKEN.value == "urn:ietf:params:oauth:token-type:access_token"
    )
    assert (
        TokenType.REFRESH_TOKEN.value
        == "urn:ietf:params:oauth:token-type:refresh_token"
    )
    assert TokenType.ID_TOKEN.value == "urn:ietf:params:oauth:token-type:id_token"
    assert TokenType.JWT.value == "urn:ietf:params:oauth:token-type:jwt"
    assert TokenType.SAML1.value == "urn:ietf:params:oauth:token-type:saml1"
    assert TokenType.SAML2.value == "urn:ietf:params:oauth:token-type:saml2"


@pytest.mark.unit
def test_token_exchange_grant_type_constant():
    """RFC 8693: Token exchange grant type constant."""
    assert (
        TOKEN_EXCHANGE_GRANT_TYPE == "urn:ietf:params:oauth:grant-type:token-exchange"
    )


@pytest.mark.unit
def test_rfc8693_spec_url():
    """RFC 8693: Spec URL should be valid."""
    assert RFC8693_SPEC_URL.startswith("https://")
    assert "8693" in RFC8693_SPEC_URL


@pytest.mark.unit
def test_include_rfc8693_router_toggle():
    """RFC 8693: include_rfc8693 respects feature flag."""
    app = FastAPI()

    with patch.object(settings, "enable_rfc8693", True):
        with patch.object(app, "include_router") as mock_include:
            include_rfc8693(app)
            mock_include.assert_called_once()

    with patch.object(settings, "enable_rfc8693", False):
        with patch.object(app, "include_router") as mock_include:
            include_rfc8693(app)
            mock_include.assert_not_called()
