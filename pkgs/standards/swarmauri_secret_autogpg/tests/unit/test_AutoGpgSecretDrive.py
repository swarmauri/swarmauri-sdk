import pytest

from swarmauri_secret_autogpg import AutoGpgSecretDrive
from swarmauri_core.crypto.types import KeyType, KeyUse


@pytest.fixture
def drv(tmp_path):
    return AutoGpgSecretDrive(key_dir=str(tmp_path / "keys"))


@pytest.mark.unit
def test_ubc_resource_and_type(drv):
    assert drv.resource == "SecretDrive"
    assert drv.type == "AutoGpgSecretDrive"


@pytest.mark.unit
def test_serialization(drv):
    assert drv.id == drv.model_validate_json(drv.model_dump_json()).id


@pytest.mark.asyncio
async def test_store_and_load_key(drv, tmp_path):
    desc = await drv.store_key(key_type=KeyType.RSA, uses=(KeyUse.WRAP,))
    assert desc.kid
    ref = await drv.load_key(kid=desc.kid, require_private=True)
    assert ref.public is not None
    assert ref.material is not None


@pytest.mark.unit
def test_encrypt_decrypt_roundtrip(drv):
    pt = b"hello secret"
    ct = drv.encrypt(pt, recipients=[str(drv.pub_path)])
    rt = drv.decrypt(ct)
    assert rt == pt
