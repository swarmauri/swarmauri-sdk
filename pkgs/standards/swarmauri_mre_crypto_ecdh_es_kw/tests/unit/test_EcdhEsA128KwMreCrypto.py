from cryptography.hazmat.primitives.asymmetric import ec
import pytest

from swarmauri_mre_crypto_ecdh_es_kw import EcdhEsA128KwMreCrypto


@pytest.fixture
def crypto() -> EcdhEsA128KwMreCrypto:
    return EcdhEsA128KwMreCrypto()


@pytest.mark.unit
def test_serialization(crypto: EcdhEsA128KwMreCrypto) -> None:
    data = crypto.model_dump_json()
    assert crypto.id == EcdhEsA128KwMreCrypto.model_validate_json(data).id


@pytest.mark.unit
@pytest.mark.asyncio
async def test_encrypt_open_roundtrip(crypto: EcdhEsA128KwMreCrypto) -> None:
    sk = ec.generate_private_key(ec.SECP256R1())
    pk = sk.public_key()
    ref = {"kid": "1", "version": 1, "kind": "cryptography_obj", "obj": pk}
    env = await crypto.encrypt_for_many([ref], b"hello")
    pt = await crypto.open_for({"kind": "cryptography_obj", "obj": sk}, env)
    assert pt == b"hello"
