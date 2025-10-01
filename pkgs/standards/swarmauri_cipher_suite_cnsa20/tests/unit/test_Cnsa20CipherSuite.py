import pytest

from swarmauri_cipher_suite_cnsa20 import Cnsa20CipherSuite


@pytest.fixture
def cipher_suite() -> Cnsa20CipherSuite:
    return Cnsa20CipherSuite()


# Standard component tests
@pytest.mark.unit
def test_ubc_resource(cipher_suite: Cnsa20CipherSuite) -> None:
    assert cipher_suite.resource == "CipherSuite"


@pytest.mark.unit
def test_ubc_type(cipher_suite: Cnsa20CipherSuite) -> None:
    assert cipher_suite.type == "Cnsa20CipherSuite"


@pytest.mark.unit
def test_initialization(cipher_suite: Cnsa20CipherSuite) -> None:
    assert isinstance(cipher_suite.id, str)


@pytest.mark.unit
def test_serialization(cipher_suite: Cnsa20CipherSuite) -> None:
    restored = Cnsa20CipherSuite.model_validate_json(cipher_suite.model_dump_json())
    assert restored.id == cipher_suite.id


@pytest.mark.unit
def test_suite_identifier(cipher_suite: Cnsa20CipherSuite) -> None:
    assert cipher_suite.suite_id() == "cnsa-2.0"


# Cipher-suite specific behavior
@pytest.mark.unit
def test_supports_expected_algorithms(cipher_suite: Cnsa20CipherSuite) -> None:
    supports = cipher_suite.supports()
    assert set(supports.keys()) == {"sign", "verify", "encrypt", "decrypt"}
    assert set(supports["sign"]) == {"ES384", "PS384"}
    assert set(supports["encrypt"]) == {"A256GCM"}
    assert supports["sign"] == supports["verify"]
    assert supports["encrypt"] == supports["decrypt"]


@pytest.mark.unit
@pytest.mark.parametrize(
    "operation, expected",
    [
        ("sign", "ES384"),
        ("verify", "A256GCM"),
        ("encrypt", "A256GCM"),
        ("decrypt", "A256GCM"),
    ],
)
def test_default_alg(
    cipher_suite: Cnsa20CipherSuite, operation: str, expected: str
) -> None:
    assert cipher_suite.default_alg(operation) == expected


@pytest.mark.unit
def test_features_descriptor(cipher_suite: Cnsa20CipherSuite) -> None:
    features = cipher_suite.features()
    assert features["suite"] == "cnsa-2.0"
    assert set(features["dialects"]["jwa"]) == {"ES384", "PS384", "A256GCM"}
    assert features["ops"]["sign"]["default"] == "ES384"
    assert features["ops"]["encrypt"]["default"] == "A256GCM"
    assert features["constraints"]["hash"] == "SHA384"


@pytest.mark.unit
def test_normalize_with_aead_defaults(cipher_suite: Cnsa20CipherSuite) -> None:
    descriptor = cipher_suite.normalize(op="encrypt", params={})

    assert descriptor["alg"] == "A256GCM"
    assert descriptor["params"]["tagBits"] == 128
    assert descriptor["params"]["nonceLen"] == 12
    assert descriptor["constraints"] == {"minKeyBits": 3072}
    assert descriptor["dialect"] == "jwa"


@pytest.mark.unit
def test_normalize_sign_preserves_params(cipher_suite: Cnsa20CipherSuite) -> None:
    descriptor = cipher_suite.normalize(
        op="sign",
        alg="PS384",
        params={"detached": True},
        dialect="custom",
    )

    assert descriptor["alg"] == "PS384"
    assert descriptor["dialect"] == "custom"
    assert descriptor["mapped"] == {"jwa": "PS384", "provider": "PS384"}
    assert descriptor["params"] == {"detached": True}


@pytest.mark.unit
def test_normalize_rejects_unsupported_alg(cipher_suite: Cnsa20CipherSuite) -> None:
    with pytest.raises(ValueError):
        cipher_suite.normalize(op="sign", alg="ES512")
