"""RFC 7952 - Security Event Token (SET) Specification.

This module provides functionality for creating, validating, and processing
Security Event Tokens (SETs) as defined in RFC 7952. SETs are JWTs that
convey security-related events between systems.

See RFC 7952: https://www.rfc-editor.org/rfc/rfc7952
"""

from __future__ import annotations

import time
import uuid
from typing import Dict, Any, Optional, List, Union


from .runtime_cfg import settings
from .rfc7519 import encode_jwt
from .jwtoken import JWTCoder
import importlib

_jwt_service_module = importlib.import_module("swarmauri_tokens_jwt.JWTTokenService")


def _allow_object_sub(
    self, payload: Dict[str, Any], subject: Any | None = None
) -> None:
    """Allow non-string ``sub`` claims as permitted by RFC 7952."""
    if subject is not None and payload.get("sub") != subject:
        raise _jwt_service_module.jwt.exceptions.InvalidSubjectError("Invalid subject")


_jwt_service_module.jwt.api_jwt.PyJWT._validate_sub = _allow_object_sub

RFC7952_SPEC_URL = "https://www.rfc-editor.org/rfc/rfc7952"

# Standard SET event types
SET_EVENT_TYPES = {
    "account-credential-change-required": (
        "https://schemas.openid.net/secevent/caep/event-type/"
        "account-credential-change-required"
    ),
    "account-purged": "https://schemas.openid.net/secevent/caep/event-type/account-purged",
    "account-disabled": "https://schemas.openid.net/secevent/caep/event-type/account-disabled",
    "account-enabled": "https://schemas.openid.net/secevent/caep/event-type/account-enabled",
    "identifier-changed": "https://schemas.openid.net/secevent/caep/event-type/identifier-changed",
    "identifier-recycled": "https://schemas.openid.net/secevent/caep/event-type/identifier-recycled",
    "session-revoked": "https://schemas.openid.net/secevent/caep/event-type/session-revoked",
    "token-claims-change": "https://schemas.openid.net/secevent/caep/event-type/token-claims-change",
}


def create_security_event_token(
    issuer: str,
    audience: Union[str, List[str]],
    event_type: str,
    subject: Dict[str, Any],
    *,
    event_data: Optional[Dict[str, Any]] = None,
    expires_in: int = 3600,
    additional_claims: Optional[Dict[str, Any]] = None,
) -> str:
    """Create a Security Event Token (SET) per RFC 7952.

    Args:
        issuer: The issuer of the SET
        audience: The intended audience(s) for the SET
        event_type: The type of security event (should be a URI)
        subject: Subject identifier(s) affected by the event
        event_data: Optional event-specific data
        expires_in: Token validity period in seconds (default: 1 hour)
        additional_claims: Optional additional claims to include

    Returns:
        SET as a JWT string

    Raises:
        RuntimeError: If RFC 7952 support is disabled
        ValueError: If required parameters are invalid
    """
    if not settings.enable_rfc7952:
        raise RuntimeError("RFC 7952 support disabled")

    if not event_type:
        raise ValueError("event_type is required")

    if not subject:
        raise ValueError("subject is required")

    current_time = int(time.time())

    # Build the events claim per RFC 7952 Section 2.2
    events_claim = {event_type: event_data or {}}

    claims = {
        "iss": issuer,
        "aud": audience,
        "iat": current_time,
        "exp": current_time + expires_in,
        "jti": str(uuid.uuid4()),
        "events": events_claim,
        "sub": subject,
    }

    if additional_claims:
        claims.update(additional_claims)

    return encode_jwt(**claims)


def validate_security_event_token(
    set_token: str,
    *,
    expected_issuer: Optional[str] = None,
    expected_audience: Optional[Union[str, List[str]]] = None,
    clock_skew_seconds: int = 30,
) -> Dict[str, Any]:
    """Validate a Security Event Token per RFC 7952.

    Args:
        set_token: The SET JWT string to validate
        expected_issuer: Expected issuer (optional)
        expected_audience: Expected audience(s) (optional)
        clock_skew_seconds: Clock skew tolerance in seconds

    Returns:
        Dict containing the validated SET claims

    Raises:
        RuntimeError: If RFC 7952 support is disabled
        ValueError: If validation fails
    """
    if not settings.enable_rfc7952:
        raise RuntimeError("RFC 7952 support disabled")

    try:
        claims = JWTCoder.default().decode(set_token, verify_exp=False)
    except Exception as e:
        raise ValueError(f"Invalid SET JWT: {e}")

    # Validate required claims per RFC 7952
    required_claims = {"iss", "aud", "iat", "exp", "events"}
    missing_claims = required_claims - set(claims.keys())
    if missing_claims:
        raise ValueError(
            f"Missing required claims: {', '.join(sorted(missing_claims))}"
        )

    # Validate issuer if specified
    if expected_issuer and claims.get("iss") != expected_issuer:
        raise ValueError(
            f"Invalid issuer: expected {expected_issuer}, got {claims.get('iss')}"
        )

    # Validate audience if specified
    if expected_audience:
        aud_claim = claims.get("aud")
        if isinstance(expected_audience, str):
            expected_audience = [expected_audience]

        if isinstance(aud_claim, str):
            aud_values = [aud_claim]
        else:
            aud_values = list(aud_claim) if aud_claim else []

        if not any(aud in expected_audience for aud in aud_values):
            raise ValueError(f"Invalid audience: {aud_values}")

    # Validate timing claims
    current_time = int(time.time())

    iat = claims.get("iat")
    if iat and iat > current_time + clock_skew_seconds:
        raise ValueError("SET issued in the future")

    exp = claims.get("exp")
    if exp and exp < current_time:
        raise ValueError("SET has expired")

    # Validate events claim structure
    events = claims.get("events")
    if not isinstance(events, dict):
        raise ValueError("'events' claim must be an object")

    if not events:
        raise ValueError("'events' claim cannot be empty")

    return claims


def extract_event_data(
    set_claims: Dict[str, Any], event_type: str
) -> Optional[Dict[str, Any]]:
    """Extract event data for a specific event type from SET claims.

    Args:
        set_claims: Validated SET claims
        event_type: The event type URI to extract

    Returns:
        Event data dictionary or None if event type not found
    """
    events = set_claims.get("events", {})
    return events.get(event_type)


def get_set_subject_identifiers(set_claims: Dict[str, Any]) -> Dict[str, Any]:
    """Extract subject identifier(s) from SET claims.

    Args:
        set_claims: Validated SET claims

    Returns:
        Subject identifier(s) dictionary
    """
    return set_claims.get("sub", {})


def create_account_disabled_set(
    issuer: str,
    audience: Union[str, List[str]],
    subject_id: str,
    reason: Optional[str] = None,
    **kwargs,
) -> str:
    """Create a SET for account disabled event.

    Args:
        issuer: The issuer of the SET
        audience: The intended audience(s)
        subject_id: The subject identifier
        reason: Optional reason for disabling
        **kwargs: Additional arguments passed to create_security_event_token

    Returns:
        SET JWT string
    """
    subject = {"format": "opaque", "id": subject_id}
    event_data = {"reason": reason} if reason else {}

    return create_security_event_token(
        issuer=issuer,
        audience=audience,
        event_type=SET_EVENT_TYPES["account-disabled"],
        subject=subject,
        event_data=event_data,
        **kwargs,
    )


def create_session_revoked_set(
    issuer: str,
    audience: Union[str, List[str]],
    subject_id: str,
    session_id: Optional[str] = None,
    **kwargs,
) -> str:
    """Create a SET for session revoked event.

    Args:
        issuer: The issuer of the SET
        audience: The intended audience(s)
        subject_id: The subject identifier
        session_id: Optional session identifier
        **kwargs: Additional arguments passed to create_security_event_token

    Returns:
        SET JWT string
    """
    subject = {"format": "opaque", "id": subject_id}
    event_data = {"session_id": session_id} if session_id else {}

    return create_security_event_token(
        issuer=issuer,
        audience=audience,
        event_type=SET_EVENT_TYPES["session-revoked"],
        subject=subject,
        event_data=event_data,
        **kwargs,
    )


__all__ = [
    "create_security_event_token",
    "validate_security_event_token",
    "extract_event_data",
    "get_set_subject_identifiers",
    "create_account_disabled_set",
    "create_session_revoked_set",
    "SET_EVENT_TYPES",
    "RFC7952_SPEC_URL",
]
