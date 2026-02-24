import pytest

from swarmauri_cipher_suite_fips205 import Fips205CipherSuite


@pytest.fixture
def cipher_suite() -> Fips205CipherSuite:
    return Fips205CipherSuite()


# Standard component tests
@pytest.mark.unit
def test_ubc_resource(cipher_suite: Fips205CipherSuite) -> None:
    assert cipher_suite.resource == "CipherSuite"


@pytest.mark.unit
def test_ubc_type(cipher_suite: Fips205CipherSuite) -> None:
    assert cipher_suite.type == "Fips205CipherSuite"


@pytest.mark.unit
def test_initialization(cipher_suite: Fips205CipherSuite) -> None:
    assert isinstance(cipher_suite.id, str)


@pytest.mark.unit
def test_serialization(cipher_suite: Fips205CipherSuite) -> None:
    restored = Fips205CipherSuite.model_validate_json(cipher_suite.model_dump_json())
    assert restored.id == cipher_suite.id


@pytest.mark.unit
def test_suite_identifier(cipher_suite: Fips205CipherSuite) -> None:
    assert cipher_suite.suite_id() == "fips-205"


# Cipher-suite specific behavior
@pytest.mark.unit
def test_supports_expected_algorithms(cipher_suite: Fips205CipherSuite) -> None:
    supports = cipher_suite.supports()
    assert set(supports.keys()) == {"sign", "verify"}
    assert tuple(supports["sign"]) == (
        "SLH-DSA-SHA2-128s",
        "SLH-DSA-SHA2-128f",
        "SLH-DSA-SHAKE-128s",
        "SLH-DSA-SHAKE-128f",
        "SLH-DSA-SHAKE-192s",
        "SLH-DSA-SHAKE-192f",
        "SLH-DSA-SHAKE-256s",
        "SLH-DSA-SHAKE-256f",
    )
    assert supports["sign"] == supports["verify"]


@pytest.mark.unit
@pytest.mark.parametrize("operation", ["sign", "verify"])
def test_default_alg(cipher_suite: Fips205CipherSuite, operation: str) -> None:
    assert cipher_suite.default_alg(operation) == "SLH-DSA-SHAKE-192s"


@pytest.mark.unit
def test_features_descriptor(cipher_suite: Fips205CipherSuite) -> None:
    features = cipher_suite.features()
    policy = cipher_suite.policy()

    assert features["suite"] == "fips-205"
    assert features["version"] == 1
    assert set(features["dialects"]["provider"]) == {
        "SLH-DSA-SHA2-128s",
        "SLH-DSA-SHA2-128f",
        "SLH-DSA-SHAKE-128s",
        "SLH-DSA-SHAKE-128f",
        "SLH-DSA-SHAKE-192s",
        "SLH-DSA-SHAKE-192f",
        "SLH-DSA-SHAKE-256s",
        "SLH-DSA-SHAKE-256f",
    }
    assert features["ops"]["sign"]["default"] == "SLH-DSA-SHAKE-192s"
    assert (
        features["constraints"]["nistSecurityLevels"] == policy["nist_security_levels"]
    )
    assert features["compliance"]["fips205"] is True


@pytest.mark.unit
def test_policy_exposes_expected_metadata(cipher_suite: Fips205CipherSuite) -> None:
    policy = cipher_suite.policy()

    assert policy["fips"] == "205"
    assert policy["nist_document"] == "SLH-DSA"
    assert policy["nist_security_levels"]["SLH-DSA-SHAKE-192s"] == 3


@pytest.mark.unit
def test_normalize_with_explicit_alg(cipher_suite: Fips205CipherSuite) -> None:
    descriptor = cipher_suite.normalize(
        op="sign",
        alg="SLH-DSA-SHA2-128s",
        params={"context": "test"},
    )

    assert descriptor["op"] == "sign"
    assert descriptor["alg"] == "SLH-DSA-SHA2-128s"
    assert descriptor["dialect"] == "provider"
    assert descriptor["mapped"] == {"provider": "slh-dsa:SLH-DSA-SHA2-128s"}
    assert descriptor["params"] == {"context": "test"}
    assert descriptor["constraints"] == {"nistLevel": 1, "category": "post-quantum"}
    assert descriptor["policy"] == cipher_suite.policy()


@pytest.mark.unit
def test_normalize_defaults(cipher_suite: Fips205CipherSuite) -> None:
    descriptor = cipher_suite.normalize(op="verify")

    assert descriptor["alg"] == "SLH-DSA-SHAKE-192s"
    assert descriptor["mapped"] == {"provider": "slh-dsa:SLH-DSA-SHAKE-192s"}


@pytest.mark.unit
def test_normalize_rejects_unsupported_alg(cipher_suite: Fips205CipherSuite) -> None:
    with pytest.raises(ValueError):
        cipher_suite.normalize(op="sign", alg="ML-DSA-44")
