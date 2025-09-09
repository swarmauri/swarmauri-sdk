"""Tests for RFC 7523: JSON Web Token (JWT) Profile for OAuth 2.0 Client Authentication and Authorization Grants.

See RFC at https://www.rfc-editor.org/rfc/rfc7523.
"""

import time
from unittest.mock import patch

import pytest

from tigrbl_auth import encode_jwt
from tigrbl_auth.errors import InvalidTokenError
from tigrbl_auth.rfc7523 import (
    RFC7523_SPEC_URL,
    validate_client_jwt_bearer,
)
from tigrbl_auth.runtime_cfg import settings


@pytest.mark.unit
def test_validate_client_jwt_bearer_success() -> None:
    """RFC 7523 §2.2: iss and sub must match for client authentication."""
    token = encode_jwt(
        iss="client",
        sub="client",
        tid="tenant",
        aud="token-endpoint",
        exp=int(time.time()) + 60,
    )
    claims = validate_client_jwt_bearer(token, audience="token-endpoint")
    assert claims["iss"] == "client"
    assert claims["sub"] == "client"
    assert RFC7523_SPEC_URL.startswith("https://")


@pytest.mark.unit
def test_validate_client_jwt_bearer_missing_claim() -> None:
    """RFC 7523 §2.2: missing required claim results in ValueError."""
    token = encode_jwt(
        iss="client",
        sub="client",
        tid="tenant",
        exp=int(time.time()) + 60,
    )
    with pytest.raises(ValueError):
        validate_client_jwt_bearer(token, audience="token-endpoint")


@pytest.mark.unit
def test_validate_client_jwt_bearer_disabled() -> None:
    """RFC 7523: validation disabled when feature is off."""
    token = encode_jwt(
        iss="client",
        sub="client",
        tid="tenant",
        aud="token-endpoint",
        exp=int(time.time()) + 60,
    )
    with patch.object(settings, "enable_rfc7523", False):
        with pytest.raises(RuntimeError):
            validate_client_jwt_bearer(token, audience="token-endpoint")


@pytest.mark.unit
def test_validate_client_jwt_bearer_mismatched_subject() -> None:
    """RFC 7523 §2.2: iss and sub must be equal."""
    token = encode_jwt(
        iss="clientA",
        sub="clientB",
        tid="tenant",
        aud="token-endpoint",
        exp=int(time.time()) + 60,
    )
    with pytest.raises(ValueError):
        validate_client_jwt_bearer(token, audience="token-endpoint")


@pytest.mark.unit
def test_validate_client_jwt_bearer_invalid_audience() -> None:
    """RFC 7523 §2.2: aud must target the token endpoint."""
    token = encode_jwt(
        iss="client",
        sub="client",
        tid="tenant",
        aud="token-endpoint",
        exp=int(time.time()) + 60,
    )
    with pytest.raises(ValueError):
        validate_client_jwt_bearer(token, audience="other-endpoint")


@pytest.mark.unit
def test_validate_client_jwt_bearer_expired_assertion() -> None:
    """RFC 7523 §2.2: exp claim must be in the future."""
    token = encode_jwt(
        iss="client",
        sub="client",
        tid="tenant",
        aud="token-endpoint",
        exp=int(time.time()) - 1,
    )
    with pytest.raises(InvalidTokenError):
        validate_client_jwt_bearer(token, audience="token-endpoint")
