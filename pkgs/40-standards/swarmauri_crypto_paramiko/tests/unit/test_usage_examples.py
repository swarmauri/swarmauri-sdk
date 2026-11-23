import paramiko
import pytest
from cryptography.hazmat.primitives import serialization

from swarmauri_crypto_paramiko import ParamikoCrypto
from swarmauri_core.crypto.types import (
    ExportPolicy,
    KeyRef,
    KeyType,
    KeyUse,
)


@pytest.mark.asyncio
@pytest.mark.example
async def test_readme_symmetric_example():
    crypto = ParamikoCrypto()
    sym = KeyRef(
        kid="sym1",
        version=1,
        type=KeyType.SYMMETRIC,
        uses=(KeyUse.ENCRYPT, KeyUse.DECRYPT),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        material=b"\x00" * 32,
    )

    ct = await crypto.encrypt(sym, b"hello")
    pt = await crypto.decrypt(sym, ct)
    assert pt == b"hello"


@pytest.mark.asyncio
@pytest.mark.example
async def test_readme_wrap_unwrap_example():
    crypto = ParamikoCrypto()
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

    wrapped = await crypto.wrap(recipient)
    unwrapped = await crypto.unwrap(recipient, wrapped)
    assert isinstance(unwrapped, bytes)
    assert len(unwrapped) == 32
