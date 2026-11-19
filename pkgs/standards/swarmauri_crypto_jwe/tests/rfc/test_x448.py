import json
from hashlib import sha256

import pytest
from cryptography.hazmat.primitives.asymmetric.x448 import X448PrivateKey
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from swarmauri_core.crypto.types import JWAAlg
from swarmauri_crypto_jwe import JweCrypto
from swarmauri_crypto_jwe.JweCrypto import _b64u, _concat_kdf

pytestmark = pytest.mark.unit

SENDER = bytes.fromhex(
    "9a8f4925d1519f5775cf46b04b5800d4ee9ee8bae8bc5565d498c28d"
    "d9c9baf574a9419744897391006382a6f127ab1d9ac2d8c0a598726b"
)
RECIPIENT = bytes.fromhex(
    "1c306a7ac2a0e2e0990b294470cba339e6453772b075811d8fad0d1d"
    "6927c120bb5ee8972b0d3e21374c9c921b09d1b0366f10b65173992d"
)
EPK = {
    "kty": "OKP",
    "crv": "X448",
    "x": (
        "mwj3zDG34-Z9ItWuoSEHSic70rg94Jxj-qc9LCLF2bvINmRyQdlT1AxbEtqIEg1"
        "TF3-A5TLEH6A"
    ),
}
Z = bytes.fromhex(
    "07fff4181ac6cc95ec1c16a94a0f74d12da232ce40a77552281d282b"
    "b60c0b56fd2464c335543936521c24403085d59a449a5037514a879d"
)


def test_rfc7518_appendix_c_concat_kdf() -> None:
    secret = bytes.fromhex(
        "9e56d91d817135d372834283bf84269cfb316ea3da806a48f6daa7798cfe90c4"
    )
    assert _concat_kdf(
        secret, JWAAlg.A128GCM, b"Alice", b"Bob"
    ) == bytes.fromhex("56aa8deaf8236d205c2228cd71a7101a")


@pytest.mark.asyncio
async def test_rfc8037_appendix_a7_x448_and_direct_jwe() -> None:
    sender = X448PrivateKey.from_private_bytes(SENDER)
    recipient = X448PrivateKey.from_private_bytes(RECIPIENT)
    assert _b64u(sender.public_key().public_bytes_raw()) == EPK["x"]
    assert sender.exchange(recipient.public_key()) == Z
    assert recipient.exchange(sender.public_key()) == Z

    # RFC 7518 direct A256GCM derivation applied to the published A.7 secret.
    cek = bytes.fromhex(
        "5171b73b1b4a7ef896ef4cb1775da5db6256dc885f260a0ae3bbe0632420bf7c"
    )
    assert _concat_kdf(Z, JWAAlg.A256GCM) == cek
    header = _b64u(
        json.dumps({"alg": "ECDH-ES", "enc": "A256GCM", "epk": EPK}).encode()
    )
    iv = bytes(12)
    sealed = AESGCM(cek).encrypt(iv, b"published X448 keys", header.encode())
    token = ".".join(
        (header, "", _b64u(iv), _b64u(sealed[:-16]), _b64u(sealed[-16:]))
    )
    with pytest.raises(ValueError, match="enable_x448"):
        await JweCrypto().decrypt_compact(token, ecdh_private_key=recipient)
    result = await JweCrypto(enable_x448=True).decrypt_compact(
        token, ecdh_private_key=recipient
    )
    assert result.plaintext == b"published X448 keys"


@pytest.mark.asyncio
async def test_x448_issuance_requires_explicit_opt_in_and_a256gcm() -> None:
    with pytest.raises(ValueError, match="enable_x448"):
        await JweCrypto().encrypt_compact(
            payload=b"", alg=JWAAlg.ECDH_ES, enc=JWAAlg.A256GCM, key=EPK
        )
    with pytest.raises(ValueError, match="A256GCM"):
        await JweCrypto(enable_x448=True).encrypt_compact(
            payload=b"", alg=JWAAlg.ECDH_ES, enc=JWAAlg.A128GCM, key=EPK
        )


@pytest.mark.asyncio
async def test_pre_fix_x25519_jwe_can_be_read_with_explicit_legacy_kdf() -> (
    None
):
    sender = X25519PrivateKey.generate()
    recipient = X25519PrivateKey.generate()
    secret = sender.exchange(recipient.public_key())
    cek = sha256(
        b"\x00\x00\x00\x01" + secret + b"\x00\x00\x00\x07A256GCM"
    ).digest()
    epk = {
        "kty": "OKP",
        "crv": "X25519",
        "x": _b64u(sender.public_key().public_bytes_raw()),
    }
    header = _b64u(
        json.dumps({"alg": "ECDH-ES", "enc": "A256GCM", "epk": epk}).encode()
    )
    iv = bytes(12)
    sealed = AESGCM(cek).encrypt(iv, b"legacy token", header.encode())
    token = ".".join(
        (header, "", _b64u(iv), _b64u(sealed[:-16]), _b64u(sealed[-16:]))
    )
    with pytest.raises(ValueError, match="invalid tag"):
        await JweCrypto().decrypt_compact(token, ecdh_private_key=recipient)
    result = await JweCrypto().decrypt_compact(
        token, ecdh_private_key=recipient, legacy_ecdh_kdf=True
    )
    assert result.plaintext == b"legacy token"
