"""Tests for RFC 7518: JSON Web Algorithms (JWA)."""

from auto_authn.v2 import supported_algorithms


def test_supported_algorithms_contains_eddsa() -> None:
    assert "EdDSA" in supported_algorithms()


def test_supported_algorithms_contains_rs256() -> None:
    assert "RS256" in supported_algorithms()
