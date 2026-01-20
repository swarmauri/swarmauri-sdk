import pytest

from swarmauri_cipher_suite_fips203 import Fips203CipherSuite


@pytest.fixture
def cipher_suite() -> Fips203CipherSuite:
    return Fips203CipherSuite()


# Standard component tests
@pytest.mark.unit
def test_ubc_resource(cipher_suite: Fips203CipherSuite) -> None:
    assert cipher_suite.resource == "CipherSuite"


@pytest.mark.unit
def test_ubc_type(cipher_suite: Fips203CipherSuite) -> None:
    assert cipher_suite.type == "Fips203CipherSuite"


@pytest.mark.unit
def test_initialization(cipher_suite: Fips203CipherSuite) -> None:
    assert isinstance(cipher_suite.id, str)


@pytest.mark.unit
def test_serialization(cipher_suite: Fips203CipherSuite) -> None:
    restored = Fips203CipherSuite.model_validate_json(cipher_suite.model_dump_json())
    assert restored.id == cipher_suite.id


@pytest.mark.unit
def test_suite_identifier(cipher_suite: Fips203CipherSuite) -> None:
    assert cipher_suite.suite_id() == "fips-203"


# Cipher-suite specific behavior
@pytest.mark.unit
def test_supports_expected_algorithms(cipher_suite: Fips203CipherSuite) -> None:
    supports = cipher_suite.supports()
    assert set(supports.keys()) == {"wrap", "unwrap"}
    assert tuple(supports["wrap"]) == ("ML-KEM-512", "ML-KEM-768", "ML-KEM-1024")
    assert supports["wrap"] == supports["unwrap"]


@pytest.mark.unit
@pytest.mark.parametrize("operation", ["wrap", "unwrap"])
def test_default_alg(cipher_suite: Fips203CipherSuite, operation: str) -> None:
    assert cipher_suite.default_alg(operation) == "ML-KEM-768"


@pytest.mark.unit
def test_features_descriptor(cipher_suite: Fips203CipherSuite) -> None:
    features = cipher_suite.features()
    policy = cipher_suite.policy()

    assert features["suite"] == "fips-203"
    assert features["version"] == 1
    assert set(features["dialects"]["provider"]) == {
        "ML-KEM-512",
        "ML-KEM-768",
        "ML-KEM-1024",
    }
    assert features["ops"]["wrap"]["default"] == "ML-KEM-768"
    assert features["constraints"]["nistSecurityLevels"] == policy[
        "nist_security_levels"
    ]
    assert features["compliance"]["fips203"] is True


@pytest.mark.unit
def test_policy_exposes_expected_metadata(cipher_suite: Fips203CipherSuite) -> None:
    policy = cipher_suite.policy()

    assert policy["fips"] == "203"
    assert policy["nist_document"] == "ML-KEM"
    assert policy["nist_security_levels"]["ML-KEM-768"] == 3


@pytest.mark.unit
def test_normalize_with_explicit_alg(cipher_suite: Fips203CipherSuite) -> None:
    descriptor = cipher_suite.normalize(
        op="wrap",
        alg="ML-KEM-1024",
        params={"context": "test"},
    )

    assert descriptor["op"] == "wrap"
    assert descriptor["alg"] == "ML-KEM-1024"
    assert descriptor["dialect"] == "provider"
    assert descriptor["mapped"] == {"provider": "ml-kem:ML-KEM-1024"}
    assert descriptor["params"] == {"context": "test"}
    assert descriptor["constraints"] == {"nistLevel": 5, "category": "post-quantum"}
    assert descriptor["policy"] == cipher_suite.policy()


@pytest.mark.unit
def test_normalize_defaults(cipher_suite: Fips203CipherSuite) -> None:
    descriptor = cipher_suite.normalize(op="unwrap")

    assert descriptor["alg"] == "ML-KEM-768"
    assert descriptor["mapped"] == {"provider": "ml-kem:ML-KEM-768"}


@pytest.mark.unit
def test_normalize_rejects_unsupported_alg(cipher_suite: Fips203CipherSuite) -> None:
    with pytest.raises(ValueError):
        cipher_suite.normalize(op="wrap", alg="ML-DSA-65")
