"""Re-export swarmauri plugin dependencies for tigrbl_auth v2 modules."""

from __future__ import annotations


# Directly import implementations from their packages rather than relying on
# plugin entry points that may not expose concrete modules. This avoids import
# errors during test execution when the plugin registry has not been
# initialized.


from swarmauri_keyprovider_file import FileKeyProvider
from swarmauri_keyprovider_local import LocalKeyProvider
from swarmauri_tokens_jwt import JWTTokenService
from swarmauri_signing_ed25519 import Ed25519EnvelopeSigner
from swarmauri_signing_jws import JwsSignerVerifier
from swarmauri_crypto_jwe import JweCrypto
from swarmauri_core.crypto.types import JWAAlg, KeyUse, ExportPolicy
from swarmauri_core.keys.types import KeyAlg, KeyClass, KeySpec

from . import pydantic as _pydantic
from . import fastapi as _fastapi
from . import sqlalchemy as _sqlalchemy
from . import tigrbl as _tigrbl

from .pydantic import *  # noqa: F401,F403
from .fastapi import *  # noqa: F401,F403
from .sqlalchemy import *  # noqa: F401,F403
from .tigrbl import *  # noqa: F401,F403

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
    *(_pydantic.__all__),
    *(_fastapi.__all__),
    *(_sqlalchemy.__all__),
    *(_tigrbl.__all__),
]
