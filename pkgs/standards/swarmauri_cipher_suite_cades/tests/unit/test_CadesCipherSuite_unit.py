import pytest

from swarmauri_cipher_suite_cades import CadesCipherSuite


@pytest.fixture
def cipher_suite() -> CadesCipherSuite:
    return CadesCipherSuite()


# Standard component tests
@pytest.mark.unit
def test_ubc_resource(cipher_suite: CadesCipherSuite) -> None:
    assert cipher_suite.resource == "CipherSuite"


@pytest.mark.unit
def test_ubc_type(cipher_suite: CadesCipherSuite) -> None:
    assert cipher_suite.type == "CadesCipherSuite"


@pytest.mark.unit
def test_initialization(cipher_suite: CadesCipherSuite) -> None:
    assert isinstance(cipher_suite.id, str)


@pytest.mark.unit
def test_serialization(cipher_suite: CadesCipherSuite) -> None:
    restored = CadesCipherSuite.model_validate_json(cipher_suite.model_dump_json())
    assert restored.id == cipher_suite.id


@pytest.mark.unit
def test_suite_identifier(cipher_suite: CadesCipherSuite) -> None:
    assert cipher_suite.suite_id() == "cades"


# Cipher-suite specific behavior
@pytest.mark.unit
def test_supports_expected_algorithms(cipher_suite: CadesCipherSuite) -> None:
    supports = cipher_suite.supports()
    assert set(supports.keys()) == {"sign", "verify"}
    assert set(supports["sign"]) == {"RSA-PSS-SHA256", "ECDSA-SHA256", "EdDSA"}
    assert supports["sign"] == supports["verify"]


@pytest.mark.unit
@pytest.mark.parametrize("operation", ["sign", "verify"])
def test_default_alg(cipher_suite: CadesCipherSuite, operation: str) -> None:
    assert cipher_suite.default_alg(operation) == "RSA-PSS-SHA256"


@pytest.mark.unit
def test_features_descriptor(cipher_suite: CadesCipherSuite) -> None:
    features = cipher_suite.features()
    assert features["suite"] == "cades"
    assert features["version"] == 1
    assert features["ops"]["sign"]["default"] == "RSA-PSS-SHA256"
    assert set(features["dialects"]["cms"]) == {
        "RSA-PSS-SHA256",
        "ECDSA-SHA256",
        "EdDSA",
    }


@pytest.mark.unit
def test_normalize_with_explicit_alg(cipher_suite: CadesCipherSuite) -> None:
    descriptor = cipher_suite.normalize(
        op="sign",
        alg="ECDSA-SHA256",
        params={"detached": True},
    )

    assert descriptor["op"] == "sign"
    assert descriptor["alg"] == "ECDSA-SHA256"
    assert descriptor["dialect"] == "cms"
    assert descriptor["mapped"] == {"cms": "ECDSA-SHA256", "provider": "ECDSA-SHA256"}
    assert descriptor["params"] == {"detached": True}
    assert descriptor["constraints"] == {}
    assert descriptor["policy"] == {}


@pytest.mark.unit
def test_normalize_rejects_unsupported_alg(cipher_suite: CadesCipherSuite) -> None:
    with pytest.raises(ValueError):
        cipher_suite.normalize(op="sign", alg="RSA-PSS-SHA512")


@pytest.mark.unit
def test_normalize_defaults(cipher_suite: CadesCipherSuite) -> None:
    descriptor = cipher_suite.normalize(op="verify")

    assert descriptor["alg"] == "RSA-PSS-SHA256"
    assert descriptor["dialect"] == "cms"
    assert descriptor["mapped"] == {
        "cms": "RSA-PSS-SHA256",
        "provider": "RSA-PSS-SHA256",
    }
    assert descriptor["params"] == {}
