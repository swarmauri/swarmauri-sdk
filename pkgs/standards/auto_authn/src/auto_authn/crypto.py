"""
auth_authn_idp.crypto
=====================
Key‑management helpers for the Auth + AuthN OIDC provider.

Goals
-----
* **Per‑tenant isolation**   – every JWKS lives inside its tenant row.  
* **Rotation friendly**      – automatic overlap / pruning of old keys.  
* **Interop**                – exposes `build_keyjar()` for pyoidc.  
"""

from __future__ import annotations

import json
import logging
import time
from datetime import datetime as dt, timezone
from typing import Dict, List, Tuple

from jwcrypto import jwk
from oic.utils.keyio import KeyBundle, KeyJar

log = logging.getLogger("auth_authn.crypto")

# --------------------------------------------------------------------------- #
# Configurable constants                                                      #
# --------------------------------------------------------------------------- #
SIG_ALG = "RS256"      # JWS alg for ID‑tokens & JWT ATs
RSA_BITS = 2048        # RSA modulus size
GRACE_SEC = 86_400     # 24 h key‑overlap before purge


# --------------------------------------------------------------------------- #
# Helpers                                                                     #
# --------------------------------------------------------------------------- #
def _epoch() -> int:
    return int(time.time())


def _new_rsa_key() -> jwk.JWK:
    """
    Generate an RSA keypair with `use=sig`, `alg=SIG_ALG`, `iat`.
    """
    key = jwk.JWK.generate(kty="RSA", size=RSA_BITS, use="sig", alg=SIG_ALG)
    # kid = thumbprint – stable & unique
    key.kid = key.thumbprint()
    key.update({"iat": _epoch()})          # non‑standard but handy
    return key


def _jwks_to_dict(jwks: jwk.JWKSet) -> Dict:
    return json.loads(jwks.export())


def _dict_to_jwks(data: str | Dict) -> jwk.JWKSet:
    if isinstance(data, str):
        data = json.loads(data)
    return jwk.JWKSet(**data)


# --------------------------------------------------------------------------- #
# Rotation                                                                    #
# --------------------------------------------------------------------------- #
def rotate_jwks(jwks_json: str, *, keep_sec: int = GRACE_SEC) -> str:
    """
    If the newest signing key is older than `keep_sec`, generates a replacement,
    keeps overlapping keys for `keep_sec`, and drops anything older.
    """
    now = _epoch()
    jwks = _dict_to_jwks(jwks_json)

    # Latest existing signing key (if any)
    sig_keys = [k for k in jwks.keys if k.get("use") == "sig"]
    newest = max(sig_keys, key=lambda k: int(k.get("iat", 0)), default=None)

    if newest and now - int(newest.get("iat", 0)) < keep_sec:
        log.debug("JWKS fresh (kid=%s); no rotation needed", newest.kid)
        return jwks_json

    # Create replacement
    new_key = _new_rsa_key()
    jwks.add(new_key)
    log.info("Generated new RSA signing key kid=%s", new_key.kid)

    # Purge stale keys
    kept: List[jwk.JWK] = []
    for k in jwks.keys:
        if k.get("use") != "sig":
            kept.append(k)
            continue
        age = now - int(k.get("iat", 0))
        if age < keep_sec:
            kept.append(k)
        else:
            log.info("Pruned old key kid=%s (age=%s s)", k.kid, age)

    fresh_jwks = jwk.JWKSet()
    for k in kept:
        fresh_jwks.add(k)
    return json.dumps(_jwks_to_dict(fresh_jwks))


def active_signing_key(jwks_json: str) -> jwk.JWK:
    """
    Return the newest signing key in the JWKS.
    """
    jwks = _dict_to_jwks(jwks_json)
    sig_keys = [k for k in jwks.keys if k.get("use") == "sig"]
    if not sig_keys:
        raise RuntimeError("JWKS contains no signing keys")
    return max(sig_keys, key=lambda k: int(k.get("iat", 0)))


# --------------------------------------------------------------------------- #
# pyoidc integration                                                          #
# --------------------------------------------------------------------------- #
def build_keyjar(jwks_json: str, *, owner: str) -> KeyJar:
    """
    Convert a tenant JWKS JSON into a pyoidc KeyJar (private + public bundles).
    """
    jwks = _dict_to_jwks(jwks_json)
    kj = KeyJar()

    priv_bundle = KeyBundle(
        keys=[json.loads(k.export(private_key=True)) for k in jwks.keys],
        owner=owner,
    )
    pub_bundle = KeyBundle(
        keys=[json.loads(k.export(private_key=False)) for k in jwks.keys],
        owner="",  # public part
    )

    kj.add_kb(owner, priv_bundle)  # used for signing
    kj.add_kb("", pub_bundle)      # exposed at /.well-known/jwks.json
    return kj


# --------------------------------------------------------------------------- #
# Bootstrap helper                                                            #
# --------------------------------------------------------------------------- #
def bootstrap_jwks() -> Tuple[str, str]:
    """
    Create an initial JWKS containing a single RSA key.
    Returns (jwks_json, active_kid).
    """
    jwks = jwk.JWKSet()
    key = _new_rsa_key()
    jwks.add(key)
    return json.dumps(_jwks_to_dict(jwks)), key.kid


# --------------------------------------------------------------------------- #
# Public exports                                                              #
# --------------------------------------------------------------------------- #
__all__ = [
    "rotate_jwks",
    "active_signing_key",
    "build_keyjar",
    "bootstrap_jwks",
]
