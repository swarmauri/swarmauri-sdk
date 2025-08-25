"""Tests for JWT-Secured Authorization Request (RFC 9101).

RFC 9101 \u00a72.1 allows OAuth 2.0 authorization requests to be encoded as
JWTs. These tests verify that request parameters round-trip through the
helpers when the feature is enabled and that usage is rejected when the
feature is disabled.
"""

import asyncio
import pytest

from auto_authn.v2 import runtime_cfg, rfc9101


@pytest.mark.unit
def test_jwt_request_round_trip(monkeypatch):
    """RFC 9101 \u00a72.1 round-trips parameters through a Request Object."""
    monkeypatch.setattr(runtime_cfg.settings, "enable_rfc9101", True)
    params = {"client_id": "abc", "scope": "read", "response_type": "code"}
    token = asyncio.run(rfc9101.create_request_object(params, secret="secret"))
    decoded = asyncio.run(rfc9101.parse_request_object(token, secret="secret"))
    assert decoded == params


@pytest.mark.unit
def test_feature_toggle_disabled(monkeypatch):
    """When disabled, helpers raise a runtime error."""
    monkeypatch.setattr(runtime_cfg.settings, "enable_rfc9101", False)
    with pytest.raises(RuntimeError):
        asyncio.run(
            rfc9101.create_request_object({"client_id": "abc"}, secret="secret")
        )
