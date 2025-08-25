"""Utilities for RFC 8037 - CFRG Elliptic Curve Diffie-Hellman and Signatures.

This module provides minimal helpers for working with Octet Key Pair (OKP)
JSON Web Keys as defined by RFC 8037. Functionality can be toggled at runtime
via :class:`auto_authn.v2.runtime_cfg.Settings`.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict
import base64

from .runtime_cfg import settings

RFC8037_SPEC_URL = "https://datatracker.ietf.org/doc/html/rfc8037"


@dataclass
class OKPKey:
    """Representation of an OKP JWK."""

    crv: str
    x: bytes


def _b64url_decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data + padding)


def parse_okp_jwk(jwk: Dict[str, str]) -> OKPKey:
    """Parse an OKP JWK when RFC 8037 support is enabled."""
    if not settings.enable_rfc8037:
        raise NotImplementedError("RFC 8037 support is disabled")
    if jwk.get("kty") != "OKP":
        raise ValueError("Expected an OKP JWK")
    crv = jwk.get("crv")
    x_b64 = jwk.get("x")
    if not crv or not x_b64:
        raise ValueError("Missing required OKP parameters")
    return OKPKey(crv=crv, x=_b64url_decode(x_b64))
