"""
autoapi_authn.crypto
====================

* Password hashing & verification            – bcrypt (12 rounds by default)
* JWT EdDSA (Ed25519) key-pair management    – PEM file on disk
* Zero-cost caching of loaded keys in-process

Environment variables
---------------------
JWT_ED25519_PRIV_PATH   path to PEM-encoded Ed25519 *private* key
                        (default: "runtime_secrets/jwt_ed25519.pem")

Security notes
--------------
• Ed25519 chosen for small key size & deterministic signatures.
• Private key never leaves this module; callers get *bytes* to feed
  into PyJWT (`jwt.encode(..., key=PRIVATE_KEY, algorithm="EdDSA")`).
• If the PEM file is missing, a fresh key-pair is generated and written
  with `0o600` permissions – suitable for container first-run.
"""

from __future__ import annotations

import os
import pathlib
from functools import lru_cache
from typing import Tuple

import bcrypt
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
)
from cryptography.hazmat.primitives import serialization

# ---------------------------------------------------------------------
# Password hashing helpers
# ---------------------------------------------------------------------
_BCRYPT_ROUNDS = 12


def hash_pw(plain: str) -> bytes:
    """Return bcrypt hash of *plain* (UTF-8 encoded)."""
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt(_BCRYPT_ROUNDS))


def verify_pw(plain: str, hashed: bytes) -> bool:
    """Constant-time verification of plaintext against stored bcrypt hash."""
    if hashed is None:
        return False
    try:
        return bcrypt.checkpw(plain.encode(), hashed)
    except (ValueError, TypeError):
        # Occurs if *hashed* is invalid bcrypt format or wrong type
        return False


# ---------------------------------------------------------------------
# JWT signing key helpers
# ---------------------------------------------------------------------
_DEFAULT_KEY_PATH = pathlib.Path(
    os.getenv("JWT_ED25519_PRIV_PATH", "runtime_secrets/jwt_ed25519.pem")
)


def _generate_keypair(path: pathlib.Path) -> Tuple[bytes, bytes]:
    """Create a new Ed25519 key-pair on disk (600 perms) & return (priv, pub)."""
    path.parent.mkdir(parents=True, exist_ok=True)

    private = Ed25519PrivateKey.generate()
    pem_priv = private.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )
    pem_pub = private.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )

    path.write_bytes(pem_priv)
    path.chmod(0o600)
    return pem_priv, pem_pub


@lru_cache(maxsize=1)
def _load_keypair() -> Tuple[bytes, bytes]:
    """Load (priv_pem, pub_pem) from disk or generate if absent."""
    if not _DEFAULT_KEY_PATH.exists():
        return _generate_keypair(_DEFAULT_KEY_PATH)

    pem_priv = _DEFAULT_KEY_PATH.read_bytes()
    private_key = serialization.load_pem_private_key(pem_priv, password=None)
    if not isinstance(private_key, Ed25519PrivateKey):
        raise RuntimeError("JWT signing key is not Ed25519")

    pem_pub = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return pem_priv, pem_pub


# public exports -------------------------------------------------------
def signing_key() -> bytes:
    """PEM-encoded Ed25519 private key for `jwt.encode(..., algorithm='EdDSA')`."""
    return _load_keypair()[0]


def public_key() -> bytes:
    """PEM-encoded Ed25519 public key (exposed via `/jwks.json`)."""
    return _load_keypair()[1]
