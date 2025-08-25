"""Utilities for OAuth 2.0 Mutual-TLS Client Authentication (RFC 8705).

This module implements helpers for certificate-bound access tokens as
specified in RFC 8705 section 3.1. When mutual TLS is used, access tokens
must contain a ``cnf`` claim with an ``x5t#S256`` member that matches the
SHA-256 thumbprint of the client's certificate.
"""

from __future__ import annotations

import base64
import hashlib
from typing import Any, Dict

from jwt.exceptions import InvalidTokenError
from cryptography import x509
from cryptography.hazmat.primitives import serialization


def thumbprint_from_cert_pem(cert_pem: bytes) -> str:
    """Return the base64url-encoded SHA-256 thumbprint of *cert_pem*.

    Parameters
    ----------
    cert_pem:
        A certificate in PEM format.
    """
    cert = x509.load_pem_x509_certificate(cert_pem)
    der = cert.public_bytes(serialization.Encoding.DER)
    digest = hashlib.sha256(der).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")


def validate_certificate_binding(
    payload: Dict[str, Any], presented_thumbprint: str
) -> None:
    """Validate *payload* against the presented certificate thumbprint.

    Raises ``InvalidTokenError`` if the token is not bound to the presented
    certificate per RFC 8705 section 3.1.
    """
    cnf = payload.get("cnf")
    if not isinstance(cnf, dict):
        raise InvalidTokenError("cnf claim required by RFC 8705")
    bound = cnf.get("x5t#S256")
    if bound != presented_thumbprint:
        raise InvalidTokenError("certificate thumbprint mismatch per RFC 8705")
