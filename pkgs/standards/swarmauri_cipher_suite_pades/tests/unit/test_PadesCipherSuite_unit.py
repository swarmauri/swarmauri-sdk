import pytest

from swarmauri_cipher_suite_pades import PadesCipherSuite


@pytest.fixture
def cipher_suite() -> PadesCipherSuite:
    return PadesCipherSuite()


# Standard component tests
@pytest.mark.unit
def test_ubc_resource(cipher_suite: PadesCipherSuite) -> None:
    assert cipher_suite.resource == "CipherSuite"


@pytest.mark.unit
def test_ubc_type(cipher_suite: PadesCipherSuite) -> None:
    assert cipher_suite.type == "PadesCipherSuite"


@pytest.mark.unit
def test_initialization(cipher_suite: PadesCipherSuite) -> None:
    assert isinstance(cipher_suite.id, str)


@pytest.mark.unit
def test_serialization(cipher_suite: PadesCipherSuite) -> None:
    restored = PadesCipherSuite.model_validate_json(cipher_suite.model_dump_json())
    assert restored.id == cipher_suite.id


@pytest.mark.unit
def test_suite_identifier(cipher_suite: PadesCipherSuite) -> None:
    assert cipher_suite.suite_id() == "pades"


# Cipher-suite specific behavior
@pytest.mark.unit
def test_supports_expected_algorithms(cipher_suite: PadesCipherSuite) -> None:
    supports = cipher_suite.supports()
    assert set(supports.keys()) == {"sign", "verify"}
    assert tuple(supports["sign"]) == ("RSA-PSS-SHA256", "ECDSA-SHA256")
    assert supports["sign"] == supports["verify"]


@pytest.mark.unit
@pytest.mark.parametrize("operation", ["sign", "verify"])
def test_default_alg(cipher_suite: PadesCipherSuite, operation: str) -> None:
    assert cipher_suite.default_alg(operation) == "RSA-PSS-SHA256"


@pytest.mark.unit
def test_features_descriptor(cipher_suite: PadesCipherSuite) -> None:
    features = cipher_suite.features()
    assert features["suite"] == "pades"
    assert features["version"] == 1
    assert features["ops"]["sign"]["default"] == "RSA-PSS-SHA256"
    assert features["dialects"]["pdfsig"] == ["RSA-PSS-SHA256", "ECDSA-SHA256"]
    assert features["constraints"]["digest"] == ["SHA256", "SHA384"]


@pytest.mark.unit
def test_normalize_with_explicit_alg(cipher_suite: PadesCipherSuite) -> None:
    descriptor = cipher_suite.normalize(
        op="sign",
        alg="ECDSA-SHA256",
        params={"tsa_required": True},
    )

    assert descriptor["op"] == "sign"
    assert descriptor["alg"] == "ECDSA-SHA256"
    assert descriptor["dialect"] == "pdfsig"
    assert descriptor["mapped"] == {
        "pdfsig": "ECDSA-SHA256",
        "provider": "ECDSA-SHA256",
    }
    assert descriptor["params"] == {"tsa_required": True}
    assert descriptor["constraints"] == {}


@pytest.mark.unit
def test_normalize_rejects_unsupported_alg(cipher_suite: PadesCipherSuite) -> None:
    with pytest.raises(ValueError):
        cipher_suite.normalize(op="sign", alg="RSA-PSS-SHA512")


@pytest.mark.unit
def test_normalize_defaults(cipher_suite: PadesCipherSuite) -> None:
    descriptor = cipher_suite.normalize(op="verify")

    assert descriptor["alg"] == "RSA-PSS-SHA256"
    assert descriptor["dialect"] == "pdfsig"
    assert descriptor["mapped"] == {
        "pdfsig": "RSA-PSS-SHA256",
        "provider": "RSA-PSS-SHA256",
    }
    assert descriptor["params"] == {}
