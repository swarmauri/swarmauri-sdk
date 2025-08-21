import asyncio

import pytest

from swarmauri_keyproviders import LocalKeyProvider
from swarmauri_core.keys.types import KeySpec, KeyAlg, KeyClass, ExportPolicy, KeyUse


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_ed25519_jwk() -> None:
    kp = LocalKeyProvider()
    spec = KeySpec(
        klass=KeyClass.asymmetric,
        alg=KeyAlg.ED25519,
        uses=(KeyUse.SIGN, KeyUse.VERIFY),
        export_policy=ExportPolicy.PUBLIC_ONLY,
    )
    ref = await kp.create_key(spec)
    jwk = await kp.get_public_jwk(ref.kid)
    assert jwk["kty"] == "OKP" and jwk["crv"] == "Ed25519"


@pytest.mark.acceptance
@pytest.mark.asyncio
async def test_random_and_hkdf() -> None:
    kp = LocalKeyProvider()
    rnd = await kp.random_bytes(16)
    assert len(rnd) == 16
    out = await kp.hkdf(b"ikm", salt=b"s", info=b"i", length=32)
    assert len(out) == 32


@pytest.mark.perf
def test_create_performance(benchmark) -> None:
    spec = KeySpec(
        klass=KeyClass.symmetric,
        alg=KeyAlg.AES256_GCM,
        uses=(KeyUse.ENCRYPT, KeyUse.DECRYPT),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
    )

    def run() -> None:
        asyncio.run(LocalKeyProvider().create_key(spec))

    benchmark(run)
