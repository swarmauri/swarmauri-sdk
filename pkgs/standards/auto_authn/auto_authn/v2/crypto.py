"""
autoapi_authn.crypto
====================

Password hashing and JWT signing key management backed by swarmauri plugins.
"""

from __future__ import annotations

import asyncio
import os
import pathlib
from functools import lru_cache
from typing import Tuple

import bcrypt
from .deps import FileKeyProvider, ExportPolicy, KeyAlg, KeyClass, KeySpec, KeyUse

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
        return False


# ---------------------------------------------------------------------
# JWT signing key helpers via swarmauri FileKeyProvider
# ---------------------------------------------------------------------
_DEFAULT_KEY_DIR = pathlib.Path(os.getenv("JWT_ED25519_KEY_DIR", "runtime_secrets"))
_KID_PATH = _DEFAULT_KEY_DIR / "jwt_ed25519.kid"
_DEFAULT_KEY_PATH = _DEFAULT_KEY_DIR / "jwt_ed25519.pem"


@lru_cache(maxsize=1)
def _provider() -> FileKeyProvider:
    return FileKeyProvider(_DEFAULT_KEY_DIR)


async def _ensure_key() -> Tuple[str, bytes, bytes]:
    kp = _provider()
    if _KID_PATH.exists():
        kid = _KID_PATH.read_text().strip()
        ref = await kp.get_key(kid, include_secret=True)
    else:
        spec = KeySpec(
            klass=KeyClass.asymmetric,
            alg=KeyAlg.ED25519,
            uses=(KeyUse.SIGN, KeyUse.VERIFY),
            export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
            label="jwt_ed25519",
        )
        ref = await kp.create_key(spec)
        _KID_PATH.parent.mkdir(parents=True, exist_ok=True)
        _KID_PATH.write_text(ref.kid)
    priv = ref.material or b""
    pub = ref.public or b""
    return ref.kid, priv, pub


@lru_cache(maxsize=1)
def _load_keypair() -> Tuple[str, bytes, bytes]:
    return asyncio.run(_ensure_key())


def signing_key() -> bytes:
    """PEM-encoded Ed25519 private key for JWTTokenService."""
    return _load_keypair()[1]


def public_key() -> bytes:
    """PEM-encoded Ed25519 public key for JWKS publication."""
    return _load_keypair()[2]
