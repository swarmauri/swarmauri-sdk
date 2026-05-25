from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
from pqcrypto.kem import kyber768
import pytest

from swarmauri_mre_crypto_age import AgeMreCrypto


@pytest.fixture
def age_crypto() -> AgeMreCrypto:
    return AgeMreCrypto()


@pytest.mark.unit
def test_serialization(age_crypto: AgeMreCrypto) -> None:
    data = age_crypto.model_dump_json()
    assert age_crypto.id == AgeMreCrypto.model_validate_json(data).id


def _hybrid_keypair() -> tuple[dict[str, object], dict[str, object]]:
    x_sk = X25519PrivateKey.generate()
    x_pk = x_sk.public_key()
    mlkem_pk, mlkem_sk = kyber768.generate_keypair()
    recipient_ref = {
        "kind": "hybrid_x25519_mlkem768",
        "x25519": {"kind": "cryptography_obj", "obj": x_pk},
        "mlkem_pk": mlkem_pk,
    }
    identity_ref = {
        "kind": "hybrid_x25519_mlkem768",
        "x25519": {"kind": "cryptography_obj", "obj": x_sk},
        "mlkem_pk": mlkem_pk,
        "mlkem_sk": mlkem_sk,
    }
    return recipient_ref, identity_ref


@pytest.mark.unit
@pytest.mark.asyncio
async def test_encrypt_open_roundtrip(age_crypto: AgeMreCrypto) -> None:
    sk = X25519PrivateKey.generate()
    pk = sk.public_key()
    ref = {"kind": "cryptography_obj", "obj": pk}
    env = await age_crypto.encrypt_for_many([ref], b"hello")
    pt = await age_crypto.open_for({"kind": "cryptography_obj", "obj": sk}, env)
    assert pt == b"hello"


@pytest.mark.unit
def test_supports_lists_hybrid(age_crypto: AgeMreCrypto) -> None:
    assert "X25519MLKEM768-SEAL" in tuple(age_crypto.supports()["recipient"])


@pytest.mark.unit
@pytest.mark.asyncio
async def test_encrypt_open_roundtrip_hybrid(age_crypto: AgeMreCrypto) -> None:
    recipient_ref, identity_ref = _hybrid_keypair()
    env = await age_crypto.encrypt_for_many(
        [recipient_ref], b"hybrid", recipient_alg="X25519MLKEM768-SEAL"
    )
    pt = await age_crypto.open_for(identity_ref, env)
    assert pt == b"hybrid"
