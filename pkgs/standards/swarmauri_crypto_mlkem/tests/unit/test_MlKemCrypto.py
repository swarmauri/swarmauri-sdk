from __future__ import annotations

import base64
import json

import pytest
from pqcrypto.kem import kyber768

from swarmauri_core.crypto.types import ExportPolicy, KeyRef, KeyType, KeyUse
from swarmauri_crypto_mlkem import MlKemCrypto
from swarmauri_crypto_composite import CompositeCrypto


@pytest.fixture()
def mlkem_crypto() -> MlKemCrypto:
    return MlKemCrypto()


@pytest.fixture()
def mlkem_keypair() -> tuple[bytes, bytes]:
    return kyber768.generate_keypair()


@pytest.fixture()
def mlkem_public_ref(mlkem_keypair: tuple[bytes, bytes]) -> KeyRef:
    public, _ = mlkem_keypair
    return KeyRef(
        kid="mlkem-key",
        version=1,
        type=KeyType.MLKEM,
        uses=(KeyUse.WRAP,),
        export_policy=ExportPolicy.PUBLIC_ONLY,
        public=public,
    )


@pytest.fixture()
def mlkem_private_ref(mlkem_keypair: tuple[bytes, bytes]) -> KeyRef:
    _, private = mlkem_keypair
    return KeyRef(
        kid="mlkem-key",
        version=1,
        type=KeyType.MLKEM,
        uses=(KeyUse.UNWRAP,),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        material=private,
    )


def _extract_shared_secret(wrapped_blob: bytes) -> bytes:
    payload = json.loads(wrapped_blob.decode("utf-8"))
    return base64.b64decode(payload["shared_secret"], validate=True)


@pytest.mark.unit
def test_supports_advertises_algorithms(mlkem_crypto: MlKemCrypto) -> None:
    supports = mlkem_crypto.supports()
    assert supports["wrap"] == ("ML-KEM-768",)
    assert supports["unwrap"] == ("ML-KEM-768",)
    assert supports["seal"] == ("ML-KEM-768",)
    assert supports["unseal"] == ("ML-KEM-768",)


@pytest.mark.asyncio
async def test_seal_unseal_roundtrip(
    mlkem_crypto: MlKemCrypto,
    mlkem_public_ref: KeyRef,
    mlkem_private_ref: KeyRef,
) -> None:
    sealed = await mlkem_crypto.seal(mlkem_public_ref, b"")
    assert isinstance(sealed, bytes)
    secret = await mlkem_crypto.unseal(mlkem_private_ref, sealed)
    assert secret == mlkem_crypto.last_shared_secret
    assert len(secret) == 32


@pytest.mark.asyncio
async def test_wrap_unwrap_roundtrip(
    mlkem_crypto: MlKemCrypto,
    mlkem_public_ref: KeyRef,
    mlkem_private_ref: KeyRef,
) -> None:
    wrapped = await mlkem_crypto.wrap(mlkem_public_ref)
    secret = await mlkem_crypto.unwrap(mlkem_private_ref, wrapped)
    stored_secret = _extract_shared_secret(wrapped.wrapped)
    assert secret == stored_secret
    assert len(secret) == 32


@pytest.mark.asyncio
async def test_rejects_non_mlkem_keys(mlkem_crypto: MlKemCrypto) -> None:
    wrong_public = KeyRef(
        kid="wrong",
        version=1,
        type=KeyType.X25519,
        uses=(KeyUse.WRAP,),
        export_policy=ExportPolicy.PUBLIC_ONLY,
        public=b"pub",
    )
    wrong_private = KeyRef(
        kid="wrong",
        version=1,
        type=KeyType.X25519,
        uses=(KeyUse.UNWRAP,),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        material=b"priv",
    )

    with pytest.raises(ValueError):
        await mlkem_crypto.seal(wrong_public, b"")
    with pytest.raises(ValueError):
        await mlkem_crypto.wrap(wrong_public)
    with pytest.raises(ValueError):
        await mlkem_crypto.unseal(wrong_private, b"ct")
    valid_public = KeyRef(
        kid="temp",
        version=1,
        type=KeyType.MLKEM,
        uses=(KeyUse.WRAP,),
        export_policy=ExportPolicy.PUBLIC_ONLY,
        public=kyber768.generate_keypair()[0],
    )
    wrapped = await mlkem_crypto.wrap(valid_public)
    with pytest.raises(ValueError):
        await mlkem_crypto.unwrap(wrong_private, wrapped)


@pytest.mark.asyncio
async def test_composite_crypto_routing(
    mlkem_public_ref: KeyRef,
    mlkem_private_ref: KeyRef,
) -> None:
    composite = CompositeCrypto([MlKemCrypto()])
    wrapped = await composite.wrap(mlkem_public_ref, wrap_alg="ML-KEM-768")
    secret = await composite.unwrap(mlkem_private_ref, wrapped)
    assert len(secret) == 32
    sealed = await composite.seal(mlkem_public_ref, b"", alg="ML-KEM-768")
    unsealed = await composite.unseal(mlkem_private_ref, sealed, alg="ML-KEM-768")
    assert len(unsealed) == 32
