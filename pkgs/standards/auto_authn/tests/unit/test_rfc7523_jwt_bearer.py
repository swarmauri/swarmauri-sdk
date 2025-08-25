"""Tests for RFC 7523: JWT Bearer Token Profile for OAuth 2.0."""

import pytest

from auto_authn.v2 import (
    create_jwt_bearer_assertion,
    verify_jwt_bearer_assertion,
    runtime_cfg,
)


@pytest.mark.unit
def test_create_and_verify_assertion(monkeypatch):
    """A JWT bearer assertion can be created and verified when enabled."""
    monkeypatch.setattr(runtime_cfg.settings, "enable_rfc7523", True)
    token = create_jwt_bearer_assertion(sub="alice")
    claims = verify_jwt_bearer_assertion(token)
    assert claims["sub"] == "alice"


@pytest.mark.unit
def test_disabled(monkeypatch):
    """Disabling RFC 7523 causes helper functions to raise."""
    monkeypatch.setattr(runtime_cfg.settings, "enable_rfc7523", False)
    with pytest.raises(RuntimeError):
        create_jwt_bearer_assertion(sub="alice")
