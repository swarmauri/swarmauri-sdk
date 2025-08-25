import asyncio


from swarmauri_core.crypto.types import JWAAlg
from swarmauri_tokens_tlsboundjwt import TlsBoundJWTTokenService, x5tS256_from_der


def test_x5t_calculation_unit():
    cert = b"unit-cert"
    thumb = x5tS256_from_der(cert)
    assert thumb == x5tS256_from_der(cert)


async def _mint_and_verify() -> bool:
    svc = TlsBoundJWTTokenService(None, client_cert_der_getter=lambda: b"unit-cert")
    token = await svc.mint({"sub": "alice"}, alg=JWAAlg.HS256)
    claims = await svc.verify(token)
    return claims["cnf"]["x5t#S256"] == x5tS256_from_der(b"unit-cert")


def test_mint_and_verify_unit():
    assert asyncio.run(_mint_and_verify())
