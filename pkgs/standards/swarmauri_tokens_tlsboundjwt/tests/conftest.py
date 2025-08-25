import json
import sys
import types

from swarmauri_core.crypto.types import JWAAlg

providers_mod = types.ModuleType("swarmauri_providers")
tokens_mod = types.ModuleType("swarmauri_providers.tokens")


class JWTTokenService:
    def __init__(self, key_provider, default_issuer=None) -> None:  # noqa: D401
        self.key_provider = key_provider

    def supports(self) -> dict:
        return {"formats": ("JWT",), "algs": (JWAAlg.HS256,)}

    async def mint(
        self,
        claims: dict,
        *,
        alg: JWAAlg,
        kid: str | None = None,
        key_version: int | None = None,
        headers: dict | None = None,
        lifetime_s: int | None = None,
        issuer: str | None = None,
        subject: str | None = None,
        audience: str | list[str] | None = None,
        scope: str | None = None,
    ) -> str:
        return json.dumps(claims)

    async def verify(
        self,
        token: str,
        *,
        issuer: str | None = None,
        audience: str | list[str] | None = None,
        leeway_s: int = 60,
    ) -> dict:
        return json.loads(token)


tokens_mod.JWTTokenService = JWTTokenService
providers_mod.tokens = tokens_mod
sys.modules.setdefault("swarmauri_providers", providers_mod)
sys.modules.setdefault("swarmauri_providers.tokens", tokens_mod)
