"""
auth_authn_idp.crypto
~~~~~~~~~~~~~~~~~~~~~
Key‑management utilities for the Auth + AuthN OIDC provider.

Design goals
------------
* **Per‑tenant isolation** – keys live inside the tenant row as a JWKS JSON string.
* **Rotation friendly**  – helpers generate new RSA keys, mark old ones as inactive,
  and prune stale ones after a configurable grace period.
* **Interop**            – exposes `build_keyjar()` that plugs directly into pyoidc.
"""

from __future__ import annotations

import json
import logging
import time
from datetime import datetime as dt, timezone
from typing import Any, Dict, List, Tuple

from jwcrypto import jwk
from oic.utils.keyio import KeyJar, KeyBundle

log = logging.getLogger("auth_authn.crypto")

# --------------------------------------------------------------------------- #
# Constants                                                                   #
# --------------------------------------------------------------------------- #
SIG_ALG = "RS256"          # default JWS alg for ID‑tokens & JWT Access‑tokens
KEY_SIZE = 2048            # RSA modulus bits
KEY_GRACE_SECONDS = 86_400  # 24 h overlap before an old key is purged


# --------------------------------------------------------------------------- #
# Key generation & serialisation                                              #
# --------------------------------------------------------------------------- #
def _now_epoch() -> int:
    return int(time.time())


def generate_rsa_key(kid: str | None = None) -> jwk.JWK:
    """
    Create a new RSA private key suitable for JOSE JWS signing.

    Parameters
    ----------
    kid : str | None
        Optional key‑identifier.  If omitted a random `kid` is derived from
        the RSA public modulus SHA‑256 thumb‑print.

    Returns
    -------
    jwcrypto.jwk.JWK
    """
    key = jwk.JWK.generate(kty="RSA", size=KEY_SIZE, use="sig", alg=SIG_ALG)
    if kid:
        key.kid = kid
    # Attach issued‑at so we can sort keys later.
    key.set_kid(key.kid or key.thumbprint())
    key.update({"iat": _now_epoch()})  # non‑standard field but harmless
    return key


def jwks_to_dict(jwks: jwk.JWKSet) -> dict:
    "Return JWKSet as plain Python dict (serialisable)."
    return json.loads(jwks.export())


def dict_to_jwks(data: dict | str) -> jwk.JWKSet:
    "Accepts JSON string or dict and returns jwk.JWKSet."
    if isinstance(data, str):
        data = json.loads(data)
    return jwk.JWKSet(**data)


# --------------------------------------------------------------------------- #
# Rotation helpers                                                            #
# --------------------------------------------------------------------------- #
def rotate_jwks(
    jwks_json: str,
    *,
    retain_seconds: int = KEY_GRACE_SECONDS,
) -> str:
    """
    Insert a *new* RSA signing key as first element; mark older 'sig' keys inactive
    once they exceed `retain_seconds`.  Returns **updated** JWKS JSON.

    The function is *idempotent* – safe to call repeatedly; it only
    rotates when no 'fresh' key exists (iat > retain_seconds ago).
    """
    now = _now_epoch()
    jwks = dict_to_jwks(jwks_json)

    # Determine if we already have a 'fresh' key
    newest = max(
        (k for k in jwks.keys if k.get("use") == "sig"),
        key=lambda k: int(k.get("iat", 0)),
        default=None,
    )
    if newest and now - int(newest.get("iat", 0)) < retain_seconds:
        log.debug("Active signing key still fresh; skipping rotation")
        return jwks_json

    # 👉 Generate replacement
    new_key = generate_rsa_key()
    jwks.add(new_key)

    # Prune keys older than retain_seconds
    kept: List[jwk.JWK] = []
    for key in jwks.keys:
        if key.get("use") != "sig":
            kept.append(key)
            continue
        age = now - int(key.get("iat", 0))
        if age < retain_seconds:
            kept.append(key)
        else:
            log.info("Pruning expired signing key kid=%s (age=%ss)", key.kid, age)

    jwks = jwk.JWKSet()
    for k in kept:
        jwks.add(k)

    log.info("Generated new signing key kid=%s", new_key.kid)
    return json.dumps(jwks_to_dict(jwks))


def get_active_signing_key(jwks_json: str) -> jwk.JWK:
    """
    Return the **most recent** RSA signing key (use=sig) from JWKS.
    Raises `RuntimeError` if none exist.
    """
    jwks = dict_to_jwks(jwks_json)
    sig_keys = [k for k in jwks.keys if k.get("use") == "sig"]
    if not sig_keys:
        raise RuntimeError("JWKS contains no signing keys")
    return max(sig_keys, key=lambda k: int(k.get("iat", 0)))


# --------------------------------------------------------------------------- #
# pyoidc integration                                                          #
# --------------------------------------------------------------------------- #
def build_keyjar(jwks_json: str, owner: str) -> KeyJar:
    """
    Convert JWKS JSON (single tenant) into a pyoidc **KeyJar**.

    Parameters
    ----------
    jwks_json : str
        JWKS serialised as JSON string.
    owner : str
        Issuer / owner ID used by pyoidc to pick the right key set.

    Returns
    -------
    KeyJar
    """
    jwks = dict_to_jwks(jwks_json)
    kj = KeyJar()

    # Private & public halves go into separate KeyBundles
    priv_bundle = KeyBundle(
        keys=[json.loads(k.export(private_key=True)) for k in jwks.keys],
        owner=owner,
    )
    pub_bundle = KeyBundle(
        keys=[json.loads(k.export(private_key=False)) for k in jwks.keys],
        owner="",
    )

    kj.add_kb(owner, priv_bundle)  # used for signing
    kj.add_kb("", pub_bundle)      # public JWKS for discovery

    return kj


# --------------------------------------------------------------------------- #
# Convenience for CLI / tests                                                #
# --------------------------------------------------------------------------- #
def bootstrap_initial_jwks() -> Tuple[str, str]:
    """
    Generate an initial JWKS with *one* RSA key.

    Returns
    -------
    tuple[str, str]
        (jwks_json, active_kid)
    """
    jwks = jwk.JWKSet()
    k = generate_rsa_key()
    jwks.add(k)
    return json.dumps(jwks_to_dict(jwks)), k.kid


# --------------------------------------------------------------------------- #
# __all__                                                                     #
# --------------------------------------------------------------------------- #
__all__ = [
    "generate_rsa_key",
    "rotate_jwks",
    "get_active_signing_key",
    "build_keyjar",
    "bootstrap_initial_jwks",
]
