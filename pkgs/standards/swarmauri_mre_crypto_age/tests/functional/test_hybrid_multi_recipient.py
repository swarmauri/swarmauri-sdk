from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
from pqcrypto.kem import kyber768
import pytest

from swarmauri_mre_crypto_age import AgeMreCrypto

HYBRID_ALG = "X25519MLKEM768-SEAL"


def _make_hybrid_refs(
    count: int,
) -> tuple[list[dict[str, object]], list[dict[str, object]]]:
    recipients: list[dict[str, object]] = []
    identities: list[dict[str, object]] = []
    for _ in range(count):
        x_sk = X25519PrivateKey.generate()
        x_pk = x_sk.public_key()
        mlkem_pk, mlkem_sk = kyber768.generate_keypair()
        recipients.append(
            {
                "kind": "hybrid_x25519_mlkem768",
                "x25519": {"kind": "cryptography_obj", "obj": x_pk},
                "mlkem_pk": mlkem_pk,
            }
        )
        identities.append(
            {
                "kind": "hybrid_x25519_mlkem768",
                "x25519": {"kind": "cryptography_obj", "obj": x_sk},
                "mlkem_pk": mlkem_pk,
                "mlkem_sk": mlkem_sk,
            }
        )
    return recipients, identities


@pytest.mark.acceptance
@pytest.mark.asyncio
async def test_hybrid_multi_recipient_roundtrip() -> None:
    crypto = AgeMreCrypto()
    recipients, identities = _make_hybrid_refs(2)
    env = await crypto.encrypt_for_many(
        recipients,
        b"hybrid-shared",
        recipient_alg=HYBRID_ALG,
    )
    assert env["recipient_alg"] == HYBRID_ALG
    assert len(env["recipients"]) == 2
    for stanza in env["recipients"]:
        assert "mlkem_pk" in stanza
        assert isinstance(stanza["header"], (bytes, bytearray))

    pt0 = await crypto.open_for(identities[0], env)
    pt1 = await crypto.open_for(identities[1], env)
    assert pt0 == b"hybrid-shared"
    assert pt1 == b"hybrid-shared"

    pt_many = await crypto.open_for_many([identities[1], identities[0]], env)
    assert pt_many == b"hybrid-shared"
