"""Tests for RFC 8523: JWT Profile for OAuth 2.0 Client Authentication and Authorization Grants.

See RFC 8523: https://www.rfc-editor.org/rfc/rfc8523
"""

import time
from unittest.mock import patch

import pytest

from tigrbl_auth.errors import InvalidTokenError
from tigrbl_auth.rfc.rfc8523 import (
    RFC8523_SPEC_URL,
    validate_enhanced_jwt_bearer,
    makeClientAssertionJwt,
    is_jwt_replay,
)
from tigrbl_auth.runtime_cfg import settings
from tigrbl_auth.rfc.rfc7519 import encode_jwt


@pytest.mark.unit
def test_validate_enhanced_jwt_bearer_success():
    """RFC 8523: Enhanced JWT bearer validation with all required claims."""
    with patch.object(settings, "enable_rfc8523", True):
        with patch.object(settings, "enable_rfc7523", True):
            token = encode_jwt(
                iss="client",
                sub="client",
                aud="token-endpoint",
                exp=int(time.time()) + 300,
                iat=int(time.time()),
                jti="unique-jwt-id-123",
                tid="tenant-1",
            )
            claims = validate_enhanced_jwt_bearer(token, audience="token-endpoint")
            assert claims["iss"] == "client"
            assert claims["sub"] == "client"
            assert claims["jti"] == "unique-jwt-id-123"
            assert "iat" in claims


@pytest.mark.unit
@pytest.mark.skip(
    "encode_jwt always includes 'iat', so this case cannot be constructed"
)
def test_validate_enhanced_jwt_bearer_missing_iat():
    """RFC 8523: Missing 'iat' claim should raise ValueError."""
    ...


@pytest.mark.unit
def test_validate_enhanced_jwt_bearer_missing_jti():
    """RFC 8523: Missing 'jti' claim should raise ValueError."""
    with patch.object(settings, "enable_rfc8523", True):
        with patch.object(settings, "enable_rfc7523", True):
            token = encode_jwt(
                iss="client",
                sub="client",
                aud="token-endpoint",
                exp=int(time.time()) + 300,
                iat=int(time.time()),
                tid="tenant-1",
            )
            with pytest.raises(ValueError, match="missing required claims"):
                validate_enhanced_jwt_bearer(token, audience="token-endpoint")


@pytest.mark.unit
def test_validate_enhanced_jwt_bearer_too_old():
    """RFC 8523: JWT too old should raise ValueError."""
    with patch.object(settings, "enable_rfc8523", True):
        with patch.object(settings, "enable_rfc7523", True):
            old_time = int(time.time()) - 400  # 400 seconds ago
            token = encode_jwt(
                iss="client",
                sub="client",
                aud="token-endpoint",
                exp=int(time.time()) + 300,
                iat=old_time,
                jti="unique-jwt-id-123",
                tid="tenant-1",
            )
            with pytest.raises(ValueError, match="JWT is too old"):
                validate_enhanced_jwt_bearer(
                    token, audience="token-endpoint", max_age_seconds=300
                )


@pytest.mark.unit
def test_validate_enhanced_jwt_bearer_future_iat():
    """RFC 8523: JWT with future 'iat' triggers decode failure."""
    with patch.object(settings, "enable_rfc8523", True):
        with patch.object(settings, "enable_rfc7523", True):
            future_time = int(time.time()) + 100  # 100 seconds in future
            token = encode_jwt(
                iss="client",
                sub="client",
                aud="token-endpoint",
                exp=int(time.time()) + 400,
                iat=future_time,
                jti="unique-jwt-id-123",
                tid="tenant-1",
            )
            with pytest.raises(InvalidTokenError):
                validate_enhanced_jwt_bearer(token, audience="token-endpoint")


@pytest.mark.unit
def test_validate_enhanced_jwt_bearer_empty_jti():
    """RFC 8523: Empty 'jti' claim should raise ValueError."""
    with patch.object(settings, "enable_rfc8523", True):
        with patch.object(settings, "enable_rfc7523", True):
            token = encode_jwt(
                iss="client",
                sub="client",
                aud="token-endpoint",
                exp=int(time.time()) + 300,
                iat=int(time.time()),
                jti="",  # Empty JTI
                tid="tenant-1",
            )
            with pytest.raises(
                ValueError, match="'jti' claim must be a non-empty string"
            ):
                validate_enhanced_jwt_bearer(token, audience="token-endpoint")


@pytest.mark.unit
def test_make_client_assertion_jwt():
    """RFC 8523: Create valid client assertion JWT."""
    with patch.object(settings, "enable_rfc8523", True):
        jwt_token = makeClientAssertionJwt(
            client_id="test-client",
            audience="https://auth.example.com/token",
            expires_in=300,
        )

        # Decode and verify the created token
        from tigrbl_auth.rfc.rfc7519 import decode_jwt

        claims = decode_jwt(jwt_token)

        assert claims["iss"] == "test-client"
        assert claims["sub"] == "test-client"
        assert claims["aud"] == "https://auth.example.com/token"
        assert "exp" in claims
        assert "iat" in claims
        assert "jti" in claims


@pytest.mark.unit
def test_make_client_assertion_jwt_with_additional_claims():
    """RFC 8523: Create JWT with additional claims."""
    with patch.object(settings, "enable_rfc8523", True):
        additional = {"custom_claim": "custom_value", "scope": "read write"}
        jwt_token = makeClientAssertionJwt(
            client_id="test-client",
            audience="https://auth.example.com/token",
            additional_claims=additional,
        )

        from tigrbl_auth.rfc.rfc7519 import decode_jwt

        claims = decode_jwt(jwt_token)

        assert claims["custom_claim"] == "custom_value"
        assert claims["scope"] == "read write"


@pytest.mark.unit
def test_make_client_assertion_jwt_disabled():
    """RFC 8523: Creating JWT when disabled should raise RuntimeError."""
    with patch.object(settings, "enable_rfc8523", False):
        with pytest.raises(RuntimeError, match="RFC 8523 support disabled"):
            makeClientAssertionJwt(
                client_id="test-client",
                audience="https://auth.example.com/token",
            )


@pytest.mark.unit
def test_validate_enhanced_jwt_bearer_disabled():
    """RFC 8523: Validation when disabled should raise RuntimeError."""
    with patch.object(settings, "enable_rfc8523", False):
        with pytest.raises(RuntimeError, match="RFC 8523 support disabled"):
            validate_enhanced_jwt_bearer("dummy-token")


@pytest.mark.unit
def test_is_jwt_replay():
    """RFC 8523: JWT replay detection placeholder."""
    # This is a placeholder test for the replay detection function
    result = is_jwt_replay("test-jti", int(time.time()), 300)
    assert result is False  # Currently always returns False


@pytest.mark.unit
def test_rfc8523_spec_url():
    """RFC 8523: Spec URL should be valid."""
    assert RFC8523_SPEC_URL.startswith("https://")
    assert "8523" in RFC8523_SPEC_URL


@pytest.mark.unit
def test_validate_enhanced_jwt_bearer_clock_skew():
    """RFC 8523: Clock skew tolerance should work correctly."""
    with patch.object(settings, "enable_rfc8523", True):
        with patch.object(settings, "enable_rfc7523", True):
            # Token issued 35 seconds ago (beyond default 30s skew)
            old_time = int(time.time()) - 35
            token = encode_jwt(
                iss="client",
                sub="client",
                aud="token-endpoint",
                exp=int(time.time()) + 300,
                iat=old_time,
                jti="unique-jwt-id-123",
                tid="tenant-1",
            )

            # Should pass with increased clock skew
            claims = validate_enhanced_jwt_bearer(
                token,
                audience="token-endpoint",
                max_age_seconds=300,
                clock_skew_seconds=60,
            )
            assert claims["iss"] == "client"


@pytest.mark.unit
def test_validate_enhanced_jwt_bearer_invalid_iat_type():
    """RFC 8523: Non-integer 'iat' claim is rejected by decoder."""
    with patch.object(settings, "enable_rfc8523", True):
        with patch.object(settings, "enable_rfc7523", True):
            token = encode_jwt(
                iss="client",
                sub="client",
                aud="token-endpoint",
                exp=int(time.time()) + 300,
                iat="not-an-integer",  # Invalid type
                jti="unique-jwt-id-123",
                tid="tenant-1",
            )
            with pytest.raises(InvalidTokenError):
                validate_enhanced_jwt_bearer(token, audience="token-endpoint")
