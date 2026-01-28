from __future__ import annotations

from tigrbl_auth import deps
from swarmauri_core.key_providers import KeyAlg
from swarmauri_tokens_jwt import JWTTokenService


def test_deps_exposes_tokens_and_key_types() -> None:
    assert deps.JWTTokenService is JWTTokenService
    assert deps.KeyAlg is KeyAlg
