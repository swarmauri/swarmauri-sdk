import asyncio
import pytest

from swarmauri_core.crypto.types import JWAAlg
from swarmauri_tokens_tlsboundjwt import TlsBoundJWTTokenService


@pytest.mark.unit
@pytest.mark.xfail(reason="Enforcing certificate requirement planned")
def test_mint_requires_client_certificate():
    """Minting without a client certificate should be rejected."""
    svc = TlsBoundJWTTokenService(None)
    with pytest.raises(ValueError):
        asyncio.run(svc.mint({"sub": "alice"}, alg=JWAAlg.HS256))
