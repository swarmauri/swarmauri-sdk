"""Proof-of-Possession Key Semantics for JWTs (RFC 7800).

Minimal helper to validate that a JWT's ``cnf`` claim references the provided
JSON Web Key. Compliance can be toggled with ``enable_rfc7800`` in
:mod:`auto_authn.v2.runtime_cfg`.
"""

from __future__ import annotations

from typing import Any, Dict

from .runtime_cfg import settings
from .rfc7638 import jwk_thumbprint

RFC7800_SPEC_URL = "https://datatracker.ietf.org/doc/html/rfc7800"


def validate_cnf_claim(payload: Dict[str, Any], jwk: Dict[str, Any]) -> bool:
    """Return True if ``payload`` proves possession of *jwk*.

    When RFC 7800 support is disabled this function returns ``True``.
    """
    if not settings.enable_rfc7800:
        return True
    try:
        cnf = payload["cnf"]
        jkt = cnf["jkt"]
    except KeyError:
        return False
    return jkt == jwk_thumbprint(jwk)


__all__ = ["validate_cnf_claim", "RFC7800_SPEC_URL"]
