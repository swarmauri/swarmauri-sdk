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
    restored = Cnsa20CipherSuite.model_validate_json(
        cipher_suite.model_dump_json()
    )
    assert restored.id == cipher_suite.id


@pytest.mark.unit
def test_suite_identifier(cipher_suite: Cnsa20CipherSuite) -> None:
    assert cipher_suite.suite_id() == "cnsa-2.0"


# Cipher-suite specific behavior
@pytest.mark.unit
def test_supports_expected_algorithms(cipher_suite: Cnsa20CipherSuite) -> None:
    supports = cipher_suite.supports()
    assert set(supports.keys()) == {
        "sign",
        "verify",
        "encrypt",
        "decrypt",
        "wrap",
        "unwrap",
    }
    assert set(supports["sign"]) == {
        "ES384",
        "PS384",
        "ML-DSA-44",
        "ML-DSA-65",
        "ML-DSA-87",
        "SLH-DSA-SHAKE-192s",
        "SLH-DSA-SHAKE-192f",
        "SLH-DSA-SHAKE-256s",
        "SLH-DSA-SHAKE-256f",
    }
    assert set(supports["encrypt"]) == {"A256GCM"}
    assert set(supports["wrap"]) == {"ML-KEM-768", "ML-KEM-1024"}
    assert supports["sign"] == supports["verify"]
    assert supports["encrypt"] == supports["decrypt"]
    assert supports["wrap"] == supports["unwrap"]


@pytest.mark.unit
@pytest.mark.parametrize(
    "operation, expected",
    [
        ("sign", "ML-DSA-65"),
        ("verify", "ML-DSA-65"),
        ("encrypt", "A256GCM"),
        ("decrypt", "A256GCM"),
        ("wrap", "ML-KEM-768"),
        ("unwrap", "ML-KEM-768"),
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
    assert "ML-DSA-65" in features["dialects"]["provider"]
    assert "ML-KEM-768" in features["dialects"]["provider"]
    assert features["ops"]["sign"]["default"] == "ML-DSA-65"
    assert features["ops"]["encrypt"]["default"] == "A256GCM"
    assert features["ops"]["wrap"]["default"] == "ML-KEM-768"
    assert features["constraints"]["hash"] == "SHA384"
    assert features["constraints"]["post_quantum_levels"]["ML-DSA-65"] == 3
    assert features["constraints"]["post_quantum_levels"]["ML-KEM-768"] == 3


@pytest.mark.unit
def test_normalize_with_aead_defaults(cipher_suite: Cnsa20CipherSuite) -> None:
    descriptor = cipher_suite.normalize(op="encrypt", params={})

    assert descriptor["alg"] == "A256GCM"
    assert descriptor["params"]["tagBits"] == 128
    assert descriptor["params"]["nonceLen"] == 12
    assert descriptor["constraints"] == {
        "aead": {"tagBits": 128, "nonceLen": 12}
    }
    assert descriptor["dialect"] == "jwa"


@pytest.mark.unit
def test_normalize_classic_sign_preserves_params(
    cipher_suite: Cnsa20CipherSuite,
) -> None:
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
def test_normalize_post_quantum_sign_defaults(
    cipher_suite: Cnsa20CipherSuite,
) -> None:
    descriptor = cipher_suite.normalize(op="sign")

    assert descriptor["alg"] == "ML-DSA-65"
    assert descriptor["dialect"] == "provider"
    assert descriptor["mapped"] == {"provider": "ML-DSA-65"}
    assert descriptor["constraints"] == {
        "nistLevel": 3,
        "category": "post-quantum",
    }


@pytest.mark.unit
def test_normalize_wrap_defaults(cipher_suite: Cnsa20CipherSuite) -> None:
    descriptor = cipher_suite.normalize(op="wrap")

    assert descriptor["alg"] == "ML-KEM-768"
    assert descriptor["dialect"] == "provider"
    assert descriptor["mapped"] == {"provider": "ML-KEM-768"}
    assert descriptor["constraints"] == {
        "nistLevel": 3,
        "category": "post-quantum",
    }


@pytest.mark.unit
def test_normalize_rejects_unsupported_alg(
    cipher_suite: Cnsa20CipherSuite,
) -> None:
    with pytest.raises(ValueError):
        cipher_suite.normalize(op="sign", alg="ES512")
