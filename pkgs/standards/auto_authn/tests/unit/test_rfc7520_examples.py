"""RFC 7520 compliance tests for JOSE examples.

These tests verify that the helper functions defined by :rfc:`7520` behave as
expected and honor the ``AUTO_AUTHN_ENABLE_RFC7520`` flag.
"""

import importlib

import base64
import secrets

import pytest

import auto_authn.rfc7520 as rfc7520
from auto_authn import (
    RFC7520_SPEC_URL,
    jws_then_jwe,
    jwe_then_jws,
)


def _generate_oct_key() -> dict:
    """Return a minimal symmetric JWK suitable for HS256/A256GCM tests."""
    secret = secrets.token_bytes(32)  # 256 bits
    jwk_key = base64.urlsafe_b64encode(secret).rstrip(b"=").decode("ascii")
    return {"kty": "oct", "k": jwk_key, "kind": "raw", "key": secret}


def test_jws_then_jwe_roundtrip() -> None:
    key = _generate_oct_key()
    message = "hello"
    token = jws_then_jwe(message, key)
    assert jwe_then_jws(token, key) == message


def test_rfc7520_disabled(monkeypatch) -> None:
    monkeypatch.setenv("AUTO_AUTHN_ENABLE_RFC7520", "0")
    import auto_authn.runtime_cfg as runtime_cfg

    importlib.reload(runtime_cfg)
    importlib.reload(rfc7520)
    key = _generate_oct_key()
    with pytest.raises(RuntimeError):
        rfc7520.jws_then_jwe("hi", key)


def test_spec_url_constant() -> None:
    assert RFC7520_SPEC_URL.endswith("rfc7520")
