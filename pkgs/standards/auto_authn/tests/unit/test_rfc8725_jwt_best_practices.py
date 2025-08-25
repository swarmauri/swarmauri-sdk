"""Tests for JWT Best Current Practices compliance with RFC 8725.

Spec URL: https://www.rfc-editor.org/rfc/rfc8725
"""

from datetime import datetime, timedelta, timezone
import base64
import json

import pytest

from auto_authn.v2.errors import InvalidTokenError

from auto_authn.v2.jwtoken import JWTCoder
from auto_authn.v2.rfc8725 import RFC8725_SPEC_URL, validate_jwt_best_practices
from auto_authn.v2.runtime_cfg import settings


@pytest.mark.unit
def test_validation_succeeds(monkeypatch):
    monkeypatch.setattr(settings, "enable_rfc8725", True)
    token = JWTCoder.default().sign(
        sub="user", tid="tenant", iss="https://issuer", aud="audience"
    )
    claims = validate_jwt_best_practices(token)
    assert claims["aud"] == "audience"
    assert RFC8725_SPEC_URL.endswith("8725")


@pytest.mark.unit
def test_rejects_none_algorithm(monkeypatch):
    monkeypatch.setattr(settings, "enable_rfc8725", True)
    payload = {
        "sub": "user",
        "tid": "tenant",
        "iss": "https://issuer",
        "aud": "audience",
        "exp": int((datetime.now(timezone.utc) + timedelta(minutes=5)).timestamp()),
    }
    header = {"alg": "none", "typ": "JWT"}

    def to_b64(obj: dict) -> str:
        return (
            base64.urlsafe_b64encode(json.dumps(obj, separators=(",", ":")).encode())
            .rstrip(b"=")
            .decode()
        )

    token = f"{to_b64(header)}.{to_b64(payload)}."
    with pytest.raises(InvalidTokenError):
        validate_jwt_best_practices(token)


@pytest.mark.unit
def test_missing_claim(monkeypatch):
    monkeypatch.setattr(settings, "enable_rfc8725", True)
    token = JWTCoder.default().sign(sub="user", tid="tenant")
    with pytest.raises(InvalidTokenError):
        validate_jwt_best_practices(token)


@pytest.mark.unit
def test_validation_skipped_when_disabled(monkeypatch):
    monkeypatch.setattr(settings, "enable_rfc8725", False)
    token = JWTCoder.default().sign(sub="user", tid="tenant")
    claims = validate_jwt_best_practices(token)
    assert claims["sub"] == "user"
