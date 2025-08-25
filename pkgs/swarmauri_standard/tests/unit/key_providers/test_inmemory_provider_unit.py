import pytest

from swarmauri_standard.key_providers import InMemoryKeyProvider
from swarmauri_base.keys import KeyProviderBase
from swarmauri_core.keys.types import KeySpec, KeyClass, KeyAlg, ExportPolicy, KeyUse


@pytest.mark.unit
@pytest.mark.asyncio
async def test_import_and_get() -> None:
    provider = InMemoryKeyProvider()
    spec = KeySpec(
        klass=KeyClass.symmetric,
        alg=KeyAlg.AES256_GCM,
        uses=(KeyUse.ENCRYPT, KeyUse.DECRYPT),
        export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
        encoding="PEM",
        private_format="PKCS8",
        public_format="SubjectPublicKeyInfo",
        encryption="NoEncryption",
    )
    material = b"s3cr3t"
    ref = await provider.import_key(spec, material)
    fetched = await provider.get_key(ref.kid)
    assert fetched.kid == ref.kid
    assert fetched.material == material


@pytest.mark.unit
def test_ubc_resource() -> None:
    provider = InMemoryKeyProvider()
    assert provider.resource == "Crypto"


@pytest.mark.unit
def test_ubc_type() -> None:
    assert InMemoryKeyProvider().type == "InMemoryKeyProvider"


@pytest.mark.unit
def test_serialization_and_name() -> None:
    provider = InMemoryKeyProvider(name="mem-provider")
    data = provider.model_dump_json()
    restored = InMemoryKeyProvider.model_validate_json(data)
    assert restored.id == provider.id
    assert restored.name == "mem-provider"
    assert restored.resource == "Crypto"


@pytest.mark.unit
def test_inheritance() -> None:
    provider = InMemoryKeyProvider()
    assert isinstance(provider, KeyProviderBase)
