from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
import pytest

from swarmauri_mre_crypto_age import AgeMreCrypto


@pytest.fixture
def age_crypto() -> AgeMreCrypto:
    return AgeMreCrypto()


@pytest.mark.unit
def test_serialization(age_crypto: AgeMreCrypto) -> None:
    data = age_crypto.model_dump_json()
    assert age_crypto.id == AgeMreCrypto.model_validate_json(data).id


@pytest.mark.unit
@pytest.mark.asyncio
async def test_encrypt_open_roundtrip(age_crypto: AgeMreCrypto) -> None:
    sk = X25519PrivateKey.generate()
    pk = sk.public_key()
    ref = {"kind": "cryptography_obj", "obj": pk}
    env = await age_crypto.encrypt_for_many([ref], b"hello")
    pt = await age_crypto.open_for({"kind": "cryptography_obj", "obj": sk}, env)
    assert pt == b"hello"
