import pytest
from swarmauri_mre_crypto_pgp import PGPMreCrypto


@pytest.fixture
def pgp_mre_crypto():
    return PGPMreCrypto()


@pytest.mark.unit
def test_resource(pgp_mre_crypto):
    assert pgp_mre_crypto.resource == "Crypto"


@pytest.mark.unit
def test_type(pgp_mre_crypto):
    assert pgp_mre_crypto.type == "PGPMreCrypto"


@pytest.mark.unit
def test_serialization(pgp_mre_crypto):
    dumped = pgp_mre_crypto.model_dump_json()
    restored = PGPMreCrypto.model_validate_json(dumped)
    assert restored.type == pgp_mre_crypto.type
