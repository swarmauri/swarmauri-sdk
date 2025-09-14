import asyncio

import pytest

from swarmauri_core.crypto.types import JWAAlg
from swarmauri_tokens_tlsboundjwt import TlsBoundJWTTokenService, x5tS256_from_der


async def _mint(svc: TlsBoundJWTTokenService) -> str:
    return await svc.mint({"sub": "bob"}, alg=JWAAlg.HS256)


def test_verify_mismatch_functional():
    svc_a = TlsBoundJWTTokenService(None, client_cert_der_getter=lambda: b"cert-a")
    token = asyncio.run(_mint(svc_a))
    svc_b = TlsBoundJWTTokenService(None, client_cert_der_getter=lambda: b"cert-b")
    with pytest.raises(ValueError):
        asyncio.run(svc_b.verify(token))


def test_missing_certificate_functional():
    svc = TlsBoundJWTTokenService(None, client_cert_der_getter=lambda: b"cert-a")
    token = asyncio.run(_mint(svc))
    svc_missing = TlsBoundJWTTokenService(None)
    with pytest.raises(ValueError):
        asyncio.run(svc_missing.verify(token))


def test_cnf_included_functional():
    svc = TlsBoundJWTTokenService(None, client_cert_der_getter=lambda: b"cert-x")
    token = asyncio.run(_mint(svc))
    claims = asyncio.run(svc.verify(token))
    assert claims["cnf"]["x5t#S256"] == x5tS256_from_der(b"cert-x")
