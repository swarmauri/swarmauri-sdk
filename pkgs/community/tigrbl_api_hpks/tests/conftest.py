from dataclasses import dataclass

import inspect

import httpx
import pytest
import pytest_asyncio
from pgpy import PGPKey, PGPUID
from pgpy.constants import (
    CompressionAlgorithm,
    HashAlgorithm,
    KeyFlags,
    PubKeyAlgorithm,
    SymmetricKeyAlgorithm,
)


@dataclass(frozen=True)
class SampleKey:
    armored: str
    binary: bytes
    fingerprint: str
    email: str


@pytest.fixture(scope="module")
def sample_key() -> SampleKey:
    key = PGPKey.new(PubKeyAlgorithm.RSAEncryptOrSign, 2048)
    uid = PGPUID.new("HPKS Example", email="user@example.com")
    key.add_uid(
        uid,
        usage={KeyFlags.Sign},
        hashes=[HashAlgorithm.SHA256],
        ciphers=[SymmetricKeyAlgorithm.AES256],
        compression=[CompressionAlgorithm.ZLIB],
    )
    armored = str(key)
    binary = bytes(key)
    fingerprint = key.fingerprint.replace(" ", "").upper()
    return SampleKey(
        armored=armored,
        binary=binary,
        fingerprint=fingerprint,
        email="user@example.com",
    )


@pytest_asyncio.fixture
async def hpks_app():
    from tigrbl_api_hpks.app import app

    init_result = app.initialize()
    if inspect.isawaitable(init_result):
        await init_result
    yield app


@pytest_asyncio.fixture
async def client(hpks_app):
    transport = httpx.ASGITransport(app=hpks_app)
    async with httpx.AsyncClient(
        transport=transport, base_url="http://testserver"
    ) as session:
        yield session


@pytest_asyncio.fixture
async def seeded_client(client: httpx.AsyncClient, sample_key: SampleKey):
    resp = await client.post(
        "/pks/add",
        data={"keytext": sample_key.armored},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    resp.raise_for_status()
    return client
