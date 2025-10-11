import pytest

from swarmauri_cipher_suite_fips204 import Fips204CipherSuite


@pytest.fixture()
def cipher_suite() -> Fips204CipherSuite:
    return Fips204CipherSuite()


# Standard component tests
@pytest.mark.unit
def test_ubc_resource(cipher_suite: Fips204CipherSuite) -> None:
    assert cipher_suite.resource == "CipherSuite"


@pytest.mark.unit
def test_ubc_type(cipher_suite: Fips204CipherSuite) -> None:
    assert cipher_suite.type == "Fips204CipherSuite"


@pytest.mark.unit
def test_initialization(cipher_suite: Fips204CipherSuite) -> None:
    assert isinstance(cipher_suite.id, str)


@pytest.mark.unit
def test_serialization(cipher_suite: Fips204CipherSuite) -> None:
    restored = Fips204CipherSuite.model_validate_json(cipher_suite.model_dump_json())
    assert restored.id == cipher_suite.id


@pytest.mark.unit
def test_suite_identifier(cipher_suite: Fips204CipherSuite) -> None:
    assert cipher_suite.suite_id() == "fips-204"


# Cipher-suite specific behavior
@pytest.mark.unit
def test_supports_expected_algorithms(cipher_suite: Fips204CipherSuite) -> None:
    supports = cipher_suite.supports()
    assert set(supports.keys()) == {"wrap", "unwrap"}
    assert set(supports["wrap"]) == {"ML-KEM-512", "ML-KEM-768", "ML-KEM-1024"}
    assert supports["wrap"] == supports["unwrap"]


@pytest.mark.unit
@pytest.mark.parametrize(
    "operation, expected",
    [("wrap", "ML-KEM-768"), ("unwrap", "ML-KEM-768")],
)
def test_default_alg(
    cipher_suite: Fips204CipherSuite, operation: str, expected: str
) -> None:
    assert cipher_suite.default_alg(operation) == expected


@pytest.mark.unit
def test_default_alg_rejects_unknown_operation(
    cipher_suite: Fips204CipherSuite,
) -> None:
    with pytest.raises(ValueError):
        cipher_suite.default_alg("sign")


@pytest.mark.unit
def test_features_descriptor(cipher_suite: Fips204CipherSuite) -> None:
    features = cipher_suite.features()
    assert features["suite"] == "fips-204"
    assert set(features["dialects"]["mlkem"]) == {
        "ML-KEM-512",
        "ML-KEM-768",
        "ML-KEM-1024",
    }
    assert features["ops"]["wrap"]["default"] == "ML-KEM-768"
    assert features["constraints"]["kemFamily"] == "ML-KEM"
    assert features["compliance"]["postQuantum"] is True


@pytest.mark.unit
def test_policy_metadata(cipher_suite: Fips204CipherSuite) -> None:
    policy = cipher_suite.policy()
    assert policy["standard"] == "FIPS 204"
    assert policy["kem"]["defaults"]["wrap"] == "ML-KEM-768"
    assert policy["kem"]["parameters"]["ML-KEM-1024"]["securityLevel"] == 5


@pytest.mark.unit
def test_normalize_defaults(cipher_suite: Fips204CipherSuite) -> None:
    descriptor = cipher_suite.normalize(op="wrap")

    assert descriptor["alg"] == "ML-KEM-768"
    assert descriptor["dialect"] == "mlkem"
    assert descriptor["params"]["kemVersion"] == "ML-KEM"
    assert descriptor["params"]["ciphertextBytes"] == 1088
    assert descriptor["constraints"]["securityLevel"] == 3
    assert descriptor["mapped"] == {"mlkem": "ML-KEM-768", "provider": "ML-KEM-768"}


@pytest.mark.unit
def test_normalize_specific_parameter(cipher_suite: Fips204CipherSuite) -> None:
    descriptor = cipher_suite.normalize(
        op="unwrap", alg="ML-KEM-1024", params={"aad": b"ctx"}
    )

    assert descriptor["alg"] == "ML-KEM-1024"
    assert descriptor["params"]["securityLevel"] == 5
    assert descriptor["params"]["ciphertextBytes"] == 1568
    assert descriptor["params"]["aad"] == b"ctx"
    assert descriptor["constraints"]["standard"] == "FIPS 204"


@pytest.mark.unit
def test_normalize_rejects_invalid_requests(cipher_suite: Fips204CipherSuite) -> None:
    with pytest.raises(ValueError):
        cipher_suite.normalize(op="wrap", alg="RSA-OAEP-256")

    with pytest.raises(ValueError):
        cipher_suite.normalize(op="sign")
