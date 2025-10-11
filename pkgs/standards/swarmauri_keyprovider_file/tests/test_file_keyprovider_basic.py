import json

import pytest

from swarmauri_keyprovider_file import FileKeyProvider
from swarmauri_core.keys.types import KeySpec, KeyClass, KeyAlg, ExportPolicy
from swarmauri_core.crypto.types import KeyUse, KeyType


@pytest.mark.asyncio
@pytest.mark.test
@pytest.mark.unit
async def test_create_and_get(tmp_path):
    provider = FileKeyProvider(tmp_path)
    spec = KeySpec(
        klass=KeyClass.symmetric,
        alg=KeyAlg.AES256_GCM,
        uses=(KeyUse.ENCRYPT,),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        encoding="PEM",
        private_format="PKCS8",
        public_format="SubjectPublicKeyInfo",
        encryption="NoEncryption",
    )
    ref = await provider.create_key(spec)
    fetched = await provider.get_key(ref.kid, include_secret=True)
    assert fetched.material is not None
    assert fetched.kid == ref.kid


@pytest.mark.asyncio
@pytest.mark.unit
async def test_create_ed25519_with_formats(tmp_path):
    provider = FileKeyProvider(tmp_path)
    spec = KeySpec(
        klass=KeyClass.asymmetric,
        alg=KeyAlg.ED25519,
        uses=(KeyUse.SIGN,),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        encoding="PEM",
        private_format="PKCS8",
        public_format="SubjectPublicKeyInfo",
        encryption="NoEncryption",
    )
    ref = await provider.create_key(spec)
    priv_path = tmp_path / "keys" / ref.kid / "v1" / "private.pem"
    assert priv_path.read_text().startswith("-----BEGIN PRIVATE KEY-----")


@pytest.mark.asyncio
@pytest.mark.unit
async def test_create_x25519_mlkem768(tmp_path):
    provider = FileKeyProvider(tmp_path)
    spec = KeySpec(
        klass=KeyClass.asymmetric,
        alg=KeyAlg.X25519MLKEM768,
        uses=(KeyUse.ENCRYPT, KeyUse.DECRYPT),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
    )
    ref = await provider.create_key(spec)
    assert ref.type == KeyType.X25519_MLKEM768
    assert ref.tags["alg"] == KeyAlg.X25519MLKEM768.value
    public_payload = json.loads(ref.public.decode("utf-8"))
    assert public_payload["kty"] == "X25519+ML-KEM-768"
    fetched = await provider.get_key(ref.kid, include_secret=True)
    assert fetched.material is not None
    secret_payload = json.loads(fetched.material.decode("utf-8"))
    assert secret_payload["mlkem768"]["secret"]


@pytest.mark.asyncio
@pytest.mark.unit
async def test_import_and_rotate_x25519_mlkem768(tmp_path):
    source = FileKeyProvider(tmp_path / "src")
    spec = KeySpec(
        klass=KeyClass.asymmetric,
        alg=KeyAlg.X25519MLKEM768,
        uses=(KeyUse.ENCRYPT, KeyUse.DECRYPT),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
    )
    created = await source.create_key(spec)
    material_ref = await source.get_key(created.kid, include_secret=True)

    importer = FileKeyProvider(tmp_path / "dst")
    imported = await importer.import_key(
        spec,
        material_ref.material,
        public=material_ref.public,
    )
    assert imported.tags["alg"] == KeyAlg.X25519MLKEM768.value
    assert imported.type == KeyType.X25519_MLKEM768
    assert imported.tags.get("imported")

    rotated = await importer.rotate_key(imported.kid)
    assert rotated.version == 2
    assert rotated.type == KeyType.X25519_MLKEM768
    jwk = await importer.get_public_jwk(imported.kid)
    assert jwk["kty"] == "X25519+ML-KEM-768"
