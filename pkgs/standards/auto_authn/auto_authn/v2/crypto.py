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
# Path to the file storing the key identifier for the JWT signing key.  Tests
# patch this path, so keep the name `_DEFAULT_KEY_PATH` for compatibility.
_DEFAULT_KEY_PATH = _DEFAULT_KEY_DIR / "jwt_ed25519.kid"


@lru_cache(maxsize=1)
def _provider() -> FileKeyProvider:
    return FileKeyProvider(_DEFAULT_KEY_DIR)


def _generate_keypair(path: pathlib.Path) -> Tuple[str, bytes, bytes]:
    """Create a new Ed25519 key pair and store its identifier at *path*."""

    async def _create() -> Tuple[str, bytes, bytes]:
        kp = _provider()
        spec = KeySpec(
            klass=KeyClass.asymmetric,
            alg=KeyAlg.ED25519,
            uses=(KeyUse.SIGN, KeyUse.VERIFY),
            export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
            label=path.stem,
        )
        ref = await kp.create_key(spec)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(ref.kid)
        os.chmod(path, 0o600)
        return ref.kid, ref.material or b"", ref.public or b""

    return asyncio.run(_create())


async def _ensure_key() -> Tuple[str, bytes, bytes]:
    kp = _provider()
    if _DEFAULT_KEY_PATH.exists():
        kid = _DEFAULT_KEY_PATH.read_text().strip()
        try:
            ref = await kp.get_key(kid, include_secret=True)
        except Exception as exc:  # pragma: no cover - defensive
            raise ValueError("invalid JWT signing key reference") from exc
    else:
        spec = KeySpec(
            klass=KeyClass.asymmetric,
            alg=KeyAlg.ED25519,
            uses=(KeyUse.SIGN, KeyUse.VERIFY),
            export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
            label="jwt_ed25519",
        )
        ref = await kp.create_key(spec)
        _DEFAULT_KEY_PATH.parent.mkdir(parents=True, exist_ok=True)
        _DEFAULT_KEY_PATH.write_text(ref.kid)
    alg = ref.tags.get("alg") if ref.tags else None
    if alg != KeyAlg.ED25519.value:
        raise RuntimeError("JWT signing key is not Ed25519")
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
