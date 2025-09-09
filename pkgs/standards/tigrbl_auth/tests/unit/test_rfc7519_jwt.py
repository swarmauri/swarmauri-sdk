"""Tests for RFC 7519: JSON Web Token (JWT)."""

from tigrbl_auth import encode_jwt, decode_jwt


def test_encode_and_decode_jwt() -> None:
    token = encode_jwt(sub="user", tid="tenant")
    payload = decode_jwt(token)
    assert payload["sub"] == "user"
    assert payload["tid"] == "tenant"
