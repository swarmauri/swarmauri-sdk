"""Tests for RFC 7521: Assertion Framework for OAuth 2.0 Client Authentication and Authorization Grants."""

import pytest

from auto_authn.v2 import extract_client_assertion, runtime_cfg


@pytest.mark.unit
def test_extract_client_assertion(monkeypatch):
    """RFC 7521 requires both client_assertion and client_assertion_type."""
    monkeypatch.setattr(runtime_cfg.settings, "enable_rfc7521", True)
    params = {
        "client_assertion": "token",
        "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
    }
    assertion, assertion_type = extract_client_assertion(params)
    assert assertion == "token"
    assert assertion_type.endswith("jwt-bearer")


@pytest.mark.unit
def test_disabled(monkeypatch):
    """When the feature is disabled a RuntimeError is raised."""
    monkeypatch.setattr(runtime_cfg.settings, "enable_rfc7521", False)
    with pytest.raises(RuntimeError):
        extract_client_assertion(
            {
                "client_assertion": "token",
                "client_assertion_type": "urn:ietf:params:oauth:client-assertion-type:jwt-bearer",
            }
        )
