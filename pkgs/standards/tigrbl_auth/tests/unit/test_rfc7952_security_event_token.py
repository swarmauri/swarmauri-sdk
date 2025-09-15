"""Tests for RFC 7952: Security Event Token (SET) Specification.

See RFC 7952: https://www.rfc-editor.org/rfc/rfc7952
"""

import time
from unittest.mock import patch

import pytest

from tigrbl_auth.rfc.rfc7952 import (
    RFC7952_SPEC_URL,
    create_security_event_token,
    validate_security_event_token,
    extract_event_data,
    get_set_subject_identifiers,
    create_account_disabled_set,
    create_session_revoked_set,
    SET_EVENT_TYPES,
)
from tigrbl_auth.runtime_cfg import settings
from tigrbl_auth.rfc.rfc7519 import decode_jwt


@pytest.mark.unit
def test_create_security_event_token_basic():
    """RFC 7952: Create basic Security Event Token."""
    with patch.object(settings, "enable_rfc7952", True):
        set_token = create_security_event_token(
            issuer="https://auth.example.com",
            audience="https://rp.example.com",
            event_type="https://example.com/event-type/account-disabled",
            subject={"format": "opaque", "id": "user123"},
            event_data={"reason": "suspicious_activity"},
        )

        # Decode and verify the SET
        claims = decode_jwt(set_token)

        assert claims["iss"] == "https://auth.example.com"
        assert claims["aud"] == "https://rp.example.com"
        assert "iat" in claims
        assert "exp" in claims
        assert "jti" in claims
        assert "events" in claims
        assert claims["sub"] == {"format": "opaque", "id": "user123"}

        # Verify events structure
        events = claims["events"]
        assert "https://example.com/event-type/account-disabled" in events
        assert (
            events["https://example.com/event-type/account-disabled"]["reason"]
            == "suspicious_activity"
        )


@pytest.mark.unit
def test_create_security_event_token_multiple_audiences():
    """RFC 7952: Create SET with multiple audiences."""
    with patch.object(settings, "enable_rfc7952", True):
        audiences = ["https://rp1.example.com", "https://rp2.example.com"]
        set_token = create_security_event_token(
            issuer="https://auth.example.com",
            audience=audiences,
            event_type="https://example.com/event-type/session-revoked",
            subject={"format": "opaque", "id": "user123"},
        )

        claims = decode_jwt(set_token)
        assert claims["aud"] == audiences


@pytest.mark.unit
def test_create_security_event_token_missing_event_type():
    """RFC 7952: Missing event_type should raise ValueError."""
    with patch.object(settings, "enable_rfc7952", True):
        with pytest.raises(ValueError, match="event_type is required"):
            create_security_event_token(
                issuer="https://auth.example.com",
                audience="https://rp.example.com",
                event_type="",  # Empty event type
                subject={"format": "opaque", "id": "user123"},
            )


@pytest.mark.unit
def test_create_security_event_token_missing_subject():
    """RFC 7952: Missing subject should raise ValueError."""
    with patch.object(settings, "enable_rfc7952", True):
        with pytest.raises(ValueError, match="subject is required"):
            create_security_event_token(
                issuer="https://auth.example.com",
                audience="https://rp.example.com",
                event_type="https://example.com/event-type/account-disabled",
                subject={},  # Empty subject
            )


@pytest.mark.unit
def test_create_security_event_token_disabled():
    """RFC 7952: Creating SET when disabled should raise RuntimeError."""
    with patch.object(settings, "enable_rfc7952", False):
        with pytest.raises(RuntimeError, match="RFC 7952 support disabled"):
            create_security_event_token(
                issuer="https://auth.example.com",
                audience="https://rp.example.com",
                event_type="https://example.com/event-type/account-disabled",
                subject={"format": "opaque", "id": "user123"},
            )


@pytest.mark.unit
def test_validate_security_event_token_success():
    """RFC 7952: Validate valid Security Event Token."""
    with patch.object(settings, "enable_rfc7952", True):
        # Create a SET first
        set_token = create_security_event_token(
            issuer="https://auth.example.com",
            audience="https://rp.example.com",
            event_type="https://example.com/event-type/account-disabled",
            subject={"format": "opaque", "id": "user123"},
        )

        # Validate it
        claims = validate_security_event_token(
            set_token,
            expected_issuer="https://auth.example.com",
            expected_audience="https://rp.example.com",
        )

        assert claims["iss"] == "https://auth.example.com"
        assert claims["aud"] == "https://rp.example.com"
        assert "events" in claims


@pytest.mark.unit
def test_validate_security_event_token_wrong_issuer():
    """RFC 7952: Wrong issuer should raise ValueError."""
    with patch.object(settings, "enable_rfc7952", True):
        set_token = create_security_event_token(
            issuer="https://auth.example.com",
            audience="https://rp.example.com",
            event_type="https://example.com/event-type/account-disabled",
            subject={"format": "opaque", "id": "user123"},
        )

        with pytest.raises(ValueError, match="Invalid issuer"):
            validate_security_event_token(
                set_token,
                expected_issuer="https://wrong.example.com",
            )


@pytest.mark.unit
def test_validate_security_event_token_wrong_audience():
    """RFC 7952: Wrong audience should raise ValueError."""
    with patch.object(settings, "enable_rfc7952", True):
        set_token = create_security_event_token(
            issuer="https://auth.example.com",
            audience="https://rp.example.com",
            event_type="https://example.com/event-type/account-disabled",
            subject={"format": "opaque", "id": "user123"},
        )

        with pytest.raises(ValueError, match="Invalid audience"):
            validate_security_event_token(
                set_token,
                expected_audience="https://wrong.example.com",
            )


@pytest.mark.unit
def test_validate_security_event_token_expired():
    """RFC 7952: Expired SET should raise ValueError."""
    with patch.object(settings, "enable_rfc7952", True):
        # Create SET with very short expiry
        set_token = create_security_event_token(
            issuer="https://auth.example.com",
            audience="https://rp.example.com",
            event_type="https://example.com/event-type/account-disabled",
            subject={"format": "opaque", "id": "user123"},
            expires_in=1,  # 1 second
        )

        # Wait for expiry
        time.sleep(2)

        with pytest.raises(ValueError, match="SET has expired"):
            validate_security_event_token(set_token)


@pytest.mark.unit
def test_validate_security_event_token_disabled():
    """RFC 7952: Validation when disabled should raise RuntimeError."""
    with patch.object(settings, "enable_rfc7952", False):
        with pytest.raises(RuntimeError, match="RFC 7952 support disabled"):
            validate_security_event_token("dummy-token")


@pytest.mark.unit
def test_extract_event_data():
    """RFC 7952: Extract event data from SET claims."""
    with patch.object(settings, "enable_rfc7952", True):
        set_token = create_security_event_token(
            issuer="https://auth.example.com",
            audience="https://rp.example.com",
            event_type="https://example.com/event-type/account-disabled",
            subject={"format": "opaque", "id": "user123"},
            event_data={
                "reason": "suspicious_activity",
                "timestamp": "2023-01-01T00:00:00Z",
            },
        )

        claims = validate_security_event_token(set_token)
        event_data = extract_event_data(
            claims, "https://example.com/event-type/account-disabled"
        )

        assert event_data is not None
        assert event_data["reason"] == "suspicious_activity"
        assert event_data["timestamp"] == "2023-01-01T00:00:00Z"


@pytest.mark.unit
def test_extract_event_data_nonexistent():
    """RFC 7952: Extract non-existent event data should return None."""
    with patch.object(settings, "enable_rfc7952", True):
        set_token = create_security_event_token(
            issuer="https://auth.example.com",
            audience="https://rp.example.com",
            event_type="https://example.com/event-type/account-disabled",
            subject={"format": "opaque", "id": "user123"},
        )

        claims = validate_security_event_token(set_token)
        event_data = extract_event_data(
            claims, "https://example.com/event-type/nonexistent"
        )

        assert event_data is None


@pytest.mark.unit
def test_get_set_subject_identifiers():
    """RFC 7952: Get subject identifiers from SET claims."""
    with patch.object(settings, "enable_rfc7952", True):
        subject = {"format": "opaque", "id": "user123", "email": "user@example.com"}
        set_token = create_security_event_token(
            issuer="https://auth.example.com",
            audience="https://rp.example.com",
            event_type="https://example.com/event-type/account-disabled",
            subject=subject,
        )

        claims = validate_security_event_token(set_token)
        extracted_subject = get_set_subject_identifiers(claims)

        assert extracted_subject == subject


@pytest.mark.unit
def test_create_account_disabled_set():
    """RFC 7952: Create account disabled SET using helper function."""
    with patch.object(settings, "enable_rfc7952", True):
        set_token = create_account_disabled_set(
            issuer="https://auth.example.com",
            audience="https://rp.example.com",
            subject_id="user123",
            reason="policy_violation",
        )

        claims = validate_security_event_token(set_token)
        event_data = extract_event_data(claims, SET_EVENT_TYPES["account-disabled"])

        assert event_data is not None
        assert event_data["reason"] == "policy_violation"
        assert claims["sub"]["id"] == "user123"


@pytest.mark.unit
def test_create_session_revoked_set():
    """RFC 7952: Create session revoked SET using helper function."""
    with patch.object(settings, "enable_rfc7952", True):
        set_token = create_session_revoked_set(
            issuer="https://auth.example.com",
            audience="https://rp.example.com",
            subject_id="user123",
            session_id="session-abc-123",
        )

        claims = validate_security_event_token(set_token)
        event_data = extract_event_data(claims, SET_EVENT_TYPES["session-revoked"])

        assert event_data is not None
        assert event_data["session_id"] == "session-abc-123"
        assert claims["sub"]["id"] == "user123"


@pytest.mark.unit
def test_set_event_types_constants():
    """RFC 7952: Verify SET event type constants are defined."""
    assert "account-disabled" in SET_EVENT_TYPES
    assert "account-enabled" in SET_EVENT_TYPES
    assert "session-revoked" in SET_EVENT_TYPES
    assert "account-purged" in SET_EVENT_TYPES

    # Verify they are proper URIs
    for event_type in SET_EVENT_TYPES.values():
        assert event_type.startswith("https://")


@pytest.mark.unit
def test_rfc7952_spec_url():
    """RFC 7952: Spec URL should be valid."""
    assert RFC7952_SPEC_URL.startswith("https://")
    assert "7952" in RFC7952_SPEC_URL


@pytest.mark.unit
def test_validate_security_event_token_empty_events():
    """RFC 7952: Empty events claim should raise ValueError."""
    with patch.object(settings, "enable_rfc7952", True):
        from tigrbl_auth.rfc.rfc7519 import encode_jwt

        # Create invalid SET with empty events
        invalid_set = encode_jwt(
            iss="https://auth.example.com",
            aud="https://rp.example.com",
            iat=int(time.time()),
            exp=int(time.time()) + 3600,
            events={},  # Empty events - invalid
        )

        with pytest.raises(ValueError, match="'events' claim cannot be empty"):
            validate_security_event_token(invalid_set)
