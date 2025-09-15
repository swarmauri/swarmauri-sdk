"""Tests for RFC 7521: Assertion Framework for OAuth 2.0 Client Authentication and Authorization Grants.

See RFC at https://www.rfc-editor.org/rfc/rfc7521.
"""

import time
from unittest.mock import patch

import pytest

from tigrbl_auth import encode_jwt
from tigrbl_auth.errors import InvalidTokenError
from tigrbl_auth.rfc.rfc7521 import (
    RFC7521_SPEC_URL,
    validate_jwt_assertion,
)
from tigrbl_auth.runtime_cfg import settings


@pytest.mark.unit
def test_validate_jwt_assertion_success() -> None:
    """RFC 7521 §3: assertions contain required claims."""
    token = encode_jwt(
        iss="issuer",
        sub="subject",
        tid="tenant",
        aud="audience",
        exp=int(time.time()) + 60,
    )
    claims = validate_jwt_assertion(token)
    assert claims["iss"] == "issuer"
    assert claims["sub"] == "subject"
    assert claims["aud"] == "audience"
    assert claims["tid"] == "tenant"
    assert RFC7521_SPEC_URL.startswith("https://")


@pytest.mark.unit
def test_validate_jwt_assertion_missing_claim() -> None:
    """RFC 7521 §3: missing required claim results in ValueError."""
    token = encode_jwt(
        iss="issuer", sub="subject", tid="tenant", exp=int(time.time()) + 60
    )
    with pytest.raises(ValueError):
        validate_jwt_assertion(token)


@pytest.mark.unit
def test_validate_jwt_assertion_expired() -> None:
    """RFC 7521 §3: expired assertions are rejected."""
    token = encode_jwt(
        iss="issuer",
        sub="subject",
        tid="tenant",
        aud="audience",
        exp=int(time.time()) - 10,
    )
    with pytest.raises(InvalidTokenError):
        validate_jwt_assertion(token)


@pytest.mark.unit
def test_validate_jwt_assertion_disabled() -> None:
    """RFC 7521: validation disabled when feature is off."""
    token = encode_jwt(
        iss="issuer",
        sub="subject",
        tid="tenant",
        aud="audience",
        exp=int(time.time()) + 60,
    )
    with patch.object(settings, "enable_rfc7521", False):
        with pytest.raises(RuntimeError):
            validate_jwt_assertion(token)
