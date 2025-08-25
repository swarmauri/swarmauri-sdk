"""Proof-of-Possession helpers for RFC 7800 compliance.

The functions in this module assist with creating and validating the ``cnf``
(claims confirmation) structure defined in :rfc:`7800`. Enforcement may be
enabled or disabled via ``enable_rfc7800`` in
:mod:`auto_authn.v2.runtime_cfg.Settings`.

See RFC 7800: https://www.rfc-editor.org/rfc/rfc7800
"""

from __future__ import annotations

from typing import Any, Dict, Final, Mapping

from .runtime_cfg import settings
from .rfc7638 import jwk_thumbprint

RFC7800_SPEC_URL: Final = "https://www.rfc-editor.org/rfc/rfc7800"


def add_cnf_claim(payload: Mapping[str, Any], jwk: Mapping[str, Any]) -> Dict[str, Any]:
    """Return a copy of *payload* with a ``cnf`` claim referencing *jwk*.

    The ``jkt`` member of the ``cnf`` claim is populated with the JWK
    thumbprint as specified by RFC 7800 §3.  This helper always performs the
    computation regardless of the feature flag to ease token creation.
    """

    augmented = dict(payload)
    cnf = dict(augmented.get("cnf", {}))
    cnf["jkt"] = jwk_thumbprint(jwk, enabled=True)
    augmented["cnf"] = cnf
    return augmented


def verify_proof_of_possession(
    payload: Mapping[str, Any], jwk: Mapping[str, Any], *, enabled: bool | None = None
) -> bool:
    """Return ``True`` if the ``cnf`` claim matches *jwk* per :rfc:`7800`.

    When the feature is disabled the function returns ``True`` to allow tokens
    without proof-of-possession requirements.
    """

    if enabled is None:
        enabled = settings.enable_rfc7800
    if not enabled:
        return True
    cnf = payload.get("cnf", {})
    jkt = cnf.get("jkt")
    if not jkt:
        return False
    expected = jwk_thumbprint(jwk, enabled=True)
    return jkt == expected


__all__ = ["add_cnf_claim", "verify_proof_of_possession", "RFC7800_SPEC_URL"]
