"""COSE Sign1 proof-of-possession implementation."""

from .cwt import CwtPoPSigner, CwtPoPVerifier

__all__ = ["CwtPoPSigner", "CwtPoPVerifier"]
