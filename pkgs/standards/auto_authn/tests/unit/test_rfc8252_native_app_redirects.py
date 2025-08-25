"""Tests for RFC 8252 compliance (OAuth 2.0 for Native Apps).

RFC 8252 section 7 restricts redirect URIs for native applications to
private-use URI schemes or loopback addresses with a dynamically chosen
port. The tests below assert that auto_authn enforces these rules.

Excerpt from RFC 8252 section 7:

    Native applications MUST use a private-use URI scheme or the loopback
    interface with an HTTP(s) scheme for redirect URIs.

This text is embedded so tests clearly reference the specification.
"""

import uuid

import pytest

from auto_authn.v2.rfc8252 import is_native_redirect_uri
from auto_authn.v2.orm.tables import Client
from auto_authn.v2.runtime_cfg import settings

RFC8252_SPEC = (
    "Native applications MUST use a private-use URI scheme or the loopback "
    "interface with an HTTP(s) scheme for redirect URIs."
)
assert RFC8252_SPEC  # include spec text for traceability


@pytest.mark.unit
def test_accepts_loopback_redirect_uri() -> None:
    """RFC 8252 §7.3 allows loopback interface redirect URIs with any port."""
    assert is_native_redirect_uri("http://127.0.0.1:49152/callback")


@pytest.mark.unit
def test_accepts_private_scheme_redirect_uri() -> None:
    """RFC 8252 §7.1 permits private-use URI scheme redirects."""
    assert is_native_redirect_uri("com.example.app:/oauth2redirect")


@pytest.mark.unit
def test_rejects_public_http_redirect_uri() -> None:
    """Public network hosts are not valid for native app redirect URIs."""
    assert not is_native_redirect_uri("http://example.com/callback")


@pytest.mark.unit
def test_client_new_enforces_rfc8252_redirects() -> None:
    """Client.new should reject redirect URIs that violate RFC 8252."""
    tenant_id = uuid.uuid4()
    with pytest.raises(ValueError):
        Client.new(
            tenant_id,
            "client1234",
            "secret",
            ["http://example.com/callback"],
        )


@pytest.mark.unit
def test_client_new_accepts_loopback_redirect() -> None:
    """Client.new accepts loopback redirect URIs per RFC 8252."""
    tenant_id = uuid.uuid4()
    client = Client.new(
        tenant_id,
        "client5678",
        "secret",
        ["http://localhost:8080/callback"],
    )
    assert client.redirect_uris == "http://localhost:8080/callback"


@pytest.mark.unit
def test_client_new_allows_public_redirect_when_disabled(monkeypatch) -> None:
    """Non-compliant redirect URIs are allowed when RFC 8252 checks are off."""
    monkeypatch.setattr(settings, "enforce_rfc8252", False)
    tenant_id = uuid.uuid4()
    client = Client.new(
        tenant_id,
        "client9999",
        "secret",
        ["http://example.com/callback"],
    )
    assert client.redirect_uris == "http://example.com/callback"
