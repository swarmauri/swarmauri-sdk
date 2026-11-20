# README Example: CompositeTokenService basic routing
import asyncio
from typing import Any, Dict, Iterable

from swarmauri_tokens_composite import CompositeTokenService


class MemoryTokenService:
    """In-memory stand-in for an async ITokenService implementation."""

    def __init__(
        self, type_name: str, formats: Iterable[str], algs: Iterable[str]
    ):
        self.type = type_name
        self._formats = tuple(formats)
        self._algs = tuple(algs)

    def supports(self) -> Dict[str, Iterable[str]]:
        return {"formats": self._formats, "algs": self._algs}

    async def mint(
        self, claims: Dict[str, Any], *, alg: str, headers=None, **_: Any
    ) -> str:
        return f"{self.type}:{alg}:{claims['sub']}"

    async def verify(self, token: str, **kwargs) -> Dict[str, Any]:
        svc, alg, sub = token.split(":", 2)
        if svc != self.type:
            raise ValueError("routed to wrong service")
        return {"sub": sub, "alg": alg, "service": svc}

    async def jwks(self) -> Dict[str, Any]:
        return {"keys": [{"kid": f"{self.type}-kid"}]}


def build_composite() -> CompositeTokenService:
    jwt_service = MemoryTokenService("JWTTokenService", ["JWT"], ["HS256"])
    ssh_service = MemoryTokenService(
        "SshCertTokenService", ["SSH-CERT"], ["ssh-ed25519"]
    )
    return CompositeTokenService([jwt_service, ssh_service])


def describe_example(result: Dict[str, Any]) -> None:
    print("JWT token:", result["jwt_token"])
    print("SSH token:", result["ssh_token"])
    print("JWT service handled mint/verify:", result["jwt_claims"]["service"])
    print("SSH service handled mint/verify:", result["ssh_claims"]["service"])
    print("JWKS keys:", {entry["kid"] for entry in result["jwks"]["keys"]})


async def main() -> Dict[str, Any]:
    composite = build_composite()

    jwt_token = await composite.mint({"sub": "alice"}, alg="HS256")
    ssh_token = await composite.mint({"sub": "bob"}, alg="ssh-ed25519")

    jwt_claims = await composite.verify(jwt_token)
    ssh_claims = await composite.verify(ssh_token)
    jwks = await composite.jwks()

    return {
        "jwt_token": jwt_token,
        "ssh_token": ssh_token,
        "jwt_claims": jwt_claims,
        "ssh_claims": ssh_claims,
        "jwks": jwks,
    }


example_result = asyncio.run(main())
describe_example(example_result)
