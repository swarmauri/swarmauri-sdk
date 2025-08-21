import pytest
from swarmauri_crypto_keyring import KeyringMreCrypto


@pytest.fixture
def keyring_crypto():
    return KeyringMreCrypto()


@pytest.mark.unit
def test_basic_properties(keyring_crypto):
    assert keyring_crypto.type == "KeyringMreCrypto"
    assert keyring_crypto.resource == "Crypto"


@pytest.mark.unit
def test_supports_structure(keyring_crypto):
    sup = keyring_crypto.supports()
    assert "payload" in sup and "recipient" in sup
