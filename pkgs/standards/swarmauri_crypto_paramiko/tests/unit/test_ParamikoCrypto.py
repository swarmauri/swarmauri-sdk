import pytest
import paramiko
from cryptography.hazmat.primitives import serialization

from swarmauri_crypto_paramiko import ParamikoCrypto
from swarmauri_core.crypto.types import ExportPolicy, KeyRef, KeyType, KeyUse
from enum import Enum


@pytest.fixture
def paramiko_crypto():
    return ParamikoCrypto()


@pytest.mark.unit
def test_ubc_resource(paramiko_crypto):
    assert paramiko_crypto.resource == "Crypto"


@pytest.mark.unit
def test_ubc_type(paramiko_crypto):
    assert paramiko_crypto.type == "ParamikoCrypto"


@pytest.mark.unit
def test_serialization(paramiko_crypto):
    assert (
        paramiko_crypto.id
        == ParamikoCrypto.model_validate_json(paramiko_crypto.model_dump_json()).id
    )


@pytest.mark.asyncio
async def test_aead_encrypt_decrypt_roundtrip(paramiko_crypto):
    sym = KeyRef(
        kid="sym1",
        version=1,
        type=KeyType.SYMMETRIC,
        uses=(KeyUse.ENCRYPT, KeyUse.DECRYPT),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        material=b"\x11" * 32,
    )

    pt = b"hello world"
    ct = await paramiko_crypto.encrypt(sym, pt)
    rt = await paramiko_crypto.decrypt(sym, ct)
    assert rt == pt


class DummyAlg(str, Enum):
    AES256_GCM = "AES256_GCM"


@pytest.mark.asyncio
async def test_enum_algorithm_normalized(paramiko_crypto):
    sym = KeyRef(
        kid="sym2",
        version=1,
        type=KeyType.SYMMETRIC,
        uses=(KeyUse.ENCRYPT, KeyUse.DECRYPT),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        material=b"\x22" * 32,
    )

    pt = b"enum alg"
    ct = await paramiko_crypto.encrypt(sym, pt, alg=DummyAlg.AES256_GCM)
    assert ct.alg == "AES-256-GCM"
    rt = await paramiko_crypto.decrypt(sym, ct)
    assert rt == pt


@pytest.mark.asyncio
async def test_encrypt_for_many_and_unwrap(paramiko_crypto):
    key = paramiko.RSAKey.generate(2048)
    pub_line = f"{key.get_name()} {key.get_base64()}\n".encode()
    priv_pem = key.key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption(),
    )

    recipient = KeyRef(
        kid="rsa1",
        version=1,
        type=KeyType.RSA,
        uses=(KeyUse.WRAP, KeyUse.UNWRAP),
        export_policy=ExportPolicy.PUBLIC_ONLY,
        public=pub_line,
        material=priv_pem,
    )

    env = await paramiko_crypto.encrypt_for_many([recipient], b"secret")
    assert env.enc_alg == "AES-256-GCM"
    assert env.nonce and env.ct and env.tag
    assert len(env.recipients) == 1

    wrapped = await paramiko_crypto.wrap(recipient)
    unwrapped = await paramiko_crypto.unwrap(recipient, wrapped)
    assert isinstance(unwrapped, bytes)
    assert len(unwrapped) == 32
