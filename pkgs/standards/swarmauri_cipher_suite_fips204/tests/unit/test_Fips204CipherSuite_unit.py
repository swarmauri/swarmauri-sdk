import pytest

from swarmauri_cipher_suite_fips204 import Fips204CipherSuite


@pytest.fixture
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
    assert set(supports.keys()) == {"sign", "verify"}
    assert tuple(supports["sign"]) == ("ML-DSA-44", "ML-DSA-65", "ML-DSA-87")
    assert supports["sign"] == supports["verify"]


@pytest.mark.unit
@pytest.mark.parametrize("operation", ["sign", "verify"])
def test_default_alg(cipher_suite: Fips204CipherSuite, operation: str) -> None:
    assert cipher_suite.default_alg(operation) == "ML-DSA-65"


@pytest.mark.unit
def test_features_descriptor(cipher_suite: Fips204CipherSuite) -> None:
    features = cipher_suite.features()
    policy = cipher_suite.policy()

    assert features["suite"] == "fips-204"
    assert features["version"] == 1
    assert set(features["dialects"]["provider"]) == {
        "ML-DSA-44",
        "ML-DSA-65",
        "ML-DSA-87",
    }
    assert features["ops"]["sign"]["default"] == "ML-DSA-65"
    assert (
        features["constraints"]["nistSecurityLevels"] == policy["nist_security_levels"]
    )
    assert features["compliance"]["fips204"] is True


@pytest.mark.unit
def test_policy_exposes_expected_metadata(cipher_suite: Fips204CipherSuite) -> None:
    policy = cipher_suite.policy()

    assert policy["fips"] == "204"
    assert policy["nist_document"] == "ML-DSA"
    assert policy["nist_security_levels"]["ML-DSA-65"] == 3


@pytest.mark.unit
def test_normalize_with_explicit_alg(cipher_suite: Fips204CipherSuite) -> None:
    descriptor = cipher_suite.normalize(
        op="sign",
        alg="ML-DSA-44",
        params={"context": "test"},
    )

    assert descriptor["op"] == "sign"
    assert descriptor["alg"] == "ML-DSA-44"
    assert descriptor["dialect"] == "provider"
    assert descriptor["mapped"] == {"provider": "ml-dsa:ML-DSA-44"}
    assert descriptor["params"] == {"context": "test"}
    assert descriptor["constraints"] == {"nistLevel": 1, "category": "post-quantum"}
    assert descriptor["policy"] == cipher_suite.policy()


@pytest.mark.unit
def test_normalize_defaults(cipher_suite: Fips204CipherSuite) -> None:
    descriptor = cipher_suite.normalize(op="verify")

    assert descriptor["alg"] == "ML-DSA-65"
    assert descriptor["mapped"] == {"provider": "ml-dsa:ML-DSA-65"}


@pytest.mark.unit
def test_normalize_rejects_unsupported_alg(cipher_suite: Fips204CipherSuite) -> None:
    with pytest.raises(ValueError):
        cipher_suite.normalize(op="sign", alg="ML-KEM-512")
