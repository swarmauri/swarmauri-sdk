"""Re-export swarmauri plugin dependencies for auto_authn v2 modules."""

from __future__ import annotations

from swarmauri.key_providers import FileKeyProvider, LocalKeyProvider
from swarmauri.tokens import JWTTokenService
from swarmauri.signings import Ed25519EnvelopeSigner, JwsSignerVerifier
from swarmauri.crypto import JweCrypto
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
