import pytest
from swarmauri_keyprovider_inmemory import InMemoryKeyProvider
from swarmauri_core.crypto.types import ExportPolicy
from swarmauri_core.key_providers.types import KeyAlg, KeyClass, KeySpec, KeyUse


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_and_get() -> None:
    provider = InMemoryKeyProvider()
    spec = KeySpec(
        klass=KeyClass.symmetric,
        alg=KeyAlg.AES256_GCM,
        uses=(KeyUse.ENCRYPT, KeyUse.DECRYPT),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
    )
    ref = await provider.create_key(spec)
    fetched = await provider.get_key(ref.kid)
    assert fetched.kid == ref.kid
    assert fetched.material == ref.material


@pytest.mark.unit
@pytest.mark.asyncio
async def test_create_key_stores_tags_and_hides_material() -> None:
    provider = InMemoryKeyProvider()
    spec = KeySpec(
        klass=KeyClass.symmetric,
        alg=KeyAlg.AES256_GCM,
        uses=(KeyUse.ENCRYPT,),
        export_policy=ExportPolicy.NONE,
        label="session-key",
        tags={"scope": "unit"},
    )
    ref = await provider.create_key(spec)
    assert ref.material is None
    assert ref.tags["label"] == "session-key"
    assert ref.tags["scope"] == "unit"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_import_key_persists_public_component() -> None:
    provider = InMemoryKeyProvider()
    spec = KeySpec(
        klass=KeyClass.asymmetric,
        alg=KeyAlg.RSA_OAEP_256,
        uses=(KeyUse.ENCRYPT,),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
    )
    ref = await provider.import_key(
        spec,
        material=b"secret-key-material",
        public=b"public-key-material",
    )
    fetched = await provider.get_key(ref.kid)
    assert fetched.public == b"public-key-material"
    assert fetched.material == b"secret-key-material"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_rotate_key_creates_new_version() -> None:
    provider = InMemoryKeyProvider()
    spec = KeySpec(
        klass=KeyClass.symmetric,
        alg=KeyAlg.AES256_GCM,
        uses=(KeyUse.ENCRYPT, KeyUse.DECRYPT),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
    )
    ref = await provider.create_key(spec)
    rotated = await provider.rotate_key(ref.kid)
    assert rotated.version == ref.version + 1
    assert rotated.kid == ref.kid
    assert rotated.material != ref.material
    assert await provider.list_versions(ref.kid) == (1, 2)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_rotate_key_missing_kid_raises() -> None:
    provider = InMemoryKeyProvider()
    with pytest.raises(KeyError):
        await provider.rotate_key("missing")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_destroy_key_removes_versions() -> None:
    provider = InMemoryKeyProvider()
    spec = KeySpec(
        klass=KeyClass.symmetric,
        alg=KeyAlg.AES256_GCM,
        uses=(KeyUse.ENCRYPT,),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
    )
    ref = await provider.create_key(spec)
    await provider.rotate_key(ref.kid)
    assert await provider.destroy_key(ref.kid, version=1)
    assert await provider.list_versions(ref.kid) == (2,)
    assert await provider.destroy_key(ref.kid)
    with pytest.raises(KeyError):
        await provider.list_versions(ref.kid)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_destroy_key_unknown_kid_returns_false() -> None:
    provider = InMemoryKeyProvider()
    assert await provider.destroy_key("missing") is False


@pytest.mark.unit
@pytest.mark.asyncio
async def test_get_key_unknown_kid_raises() -> None:
    provider = InMemoryKeyProvider()
    with pytest.raises(KeyError):
        await provider.get_key("missing")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_list_versions_unknown_kid_raises() -> None:
    provider = InMemoryKeyProvider()
    with pytest.raises(KeyError):
        await provider.list_versions("missing")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_random_bytes_and_hkdf() -> None:
    provider = InMemoryKeyProvider()
    rand = await provider.random_bytes(24)
    assert len(rand) == 24
    okm_first = await provider.hkdf(b"ikm", salt=b"salt", info=b"ctx", length=32)
    okm_second = await provider.hkdf(b"ikm", salt=b"salt", info=b"ctx", length=32)
    okm_other = await provider.hkdf(b"ikm", salt=b"salt2", info=b"ctx", length=32)
    assert okm_first == okm_second
    assert okm_first != okm_other


@pytest.mark.unit
def test_type() -> None:
    assert InMemoryKeyProvider().type == "InMemoryKeyProvider"
