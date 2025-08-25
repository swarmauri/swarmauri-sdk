"""Re-export swarmauri plugin dependencies for auto_authn v2 modules."""

from __future__ import annotations

from swarmauri_keyprovider_file import FileKeyProvider
from swarmauri_keyprovider_local import LocalKeyProvider
from swarmauri_tokens_jwt import JWTTokenService
from swarmauri_signing_ed25519 import Ed25519EnvelopeSigner
from swarmauri_signing_jws import JwsSignerVerifier
from swarmauri_crypto_jwe import JweCrypto
from swarmauri_core.crypto.types import JWAAlg, KeyUse, ExportPolicy
from swarmauri_core.keys.types import KeyAlg, KeyClass, KeySpec

__all__ = [
    "FileKeyProvider",
    "LocalKeyProvider",
    "JWTTokenService",
    "Ed25519EnvelopeSigner",
    "JwsSignerVerifier",
    "JweCrypto",
    "JWAAlg",
    "KeyUse",
    "ExportPolicy",
    "KeyAlg",
    "KeyClass",
    "KeySpec",
]
