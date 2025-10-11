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
    assert cipher_suite.suite_id() == "fips205-slh-dsa"


# Cipher-suite specific behavior
@pytest.mark.unit
def test_supports_expected_algorithms(cipher_suite: Fips205CipherSuite) -> None:
    supports = cipher_suite.supports()
    assert set(supports.keys()) == {"sign", "verify"}
    assert tuple(supports["sign"]) == tuple(supports["verify"])
    assert supports["sign"][0] == "SLH-DSA-SHA2-128s"
    assert "SLH-DSA-SHAKE-256f" in supports["sign"]


@pytest.mark.unit
@pytest.mark.parametrize(
    ("operation", "expected"),
    [
        ("sign", "SLH-DSA-SHA2-128s"),
        ("verify", "SLH-DSA-SHA2-128s"),
    ],
)
def test_default_alg(
    cipher_suite: Fips205CipherSuite, operation: str, expected: str
) -> None:
    assert cipher_suite.default_alg(operation) == expected


@pytest.mark.unit
def test_default_alg_rejects_unknown_operation(
    cipher_suite: Fips205CipherSuite,
) -> None:
    with pytest.raises(ValueError):
        cipher_suite.default_alg("encrypt")


@pytest.mark.unit
def test_policy_exposes_metadata(cipher_suite: Fips205CipherSuite) -> None:
    policy = cipher_suite.policy()

    assert policy["fips"] is True
    assert policy["standard"] == "FIPS 205"
    assert policy["stateless"] is True
    assert "SLH-DSA-SHA2-192f" in policy["algorithms"]
    assert policy["algorithms"]["SLH-DSA-SHA2-192f"]["category"] == 3
    assert sorted(policy["hash_families"]) == [
        "SHA2-256",
        "SHA2-384",
        "SHA2-512",
        "SHAKE128",
        "SHAKE256",
    ]


@pytest.mark.unit
def test_features_descriptor(cipher_suite: Fips205CipherSuite) -> None:
    features = cipher_suite.features()

    assert features["suite"] == "fips205-slh-dsa"
    assert features["version"] == 1
    assert set(features["dialects"]["slh-dsa"]) == set(cipher_suite.supports()["sign"])
    assert features["ops"]["sign"]["default"] == "SLH-DSA-SHA2-128s"
    assert features["constraints"]["stateless"] is True
    assert features["constraints"]["signatureBytes"]["SLH-DSA-SHAKE-256f"] == 49856
    assert features["compliance"]["fips205"] is True


@pytest.mark.unit
def test_normalize_with_defaults(cipher_suite: Fips205CipherSuite) -> None:
    descriptor = cipher_suite.normalize(op="sign")

    assert descriptor["op"] == "sign"
    assert descriptor["alg"] == "SLH-DSA-SHA2-128s"
    assert descriptor["dialect"] == "slh-dsa"
    assert descriptor["mapped"] == {
        "slh-dsa": "SLH-DSA-SHA2-128s",
        "provider": "SLH-DSA-SHA2-128s",
    }
    assert descriptor["params"]["hash"] == "SHA2-256"
    assert descriptor["params"]["securityCategory"] == 1
    assert descriptor["constraints"]["securityCategory"] == 1
    assert descriptor["policy"]["standard"] == "FIPS 205"


@pytest.mark.unit
def test_normalize_accepts_specific_algorithm(cipher_suite: Fips205CipherSuite) -> None:
    descriptor = cipher_suite.normalize(op="sign", alg="SLH-DSA-SHAKE-256f", params={})

    assert descriptor["alg"] == "SLH-DSA-SHAKE-256f"
    assert descriptor["params"]["hash"] == "SHAKE256"
    assert descriptor["params"]["variant"] == "fast"
    assert descriptor["params"]["signatureBytes"] == 49856
    assert descriptor["constraints"]["stateless"] is True


@pytest.mark.unit
def test_normalize_rejects_unknown_algorithm(cipher_suite: Fips205CipherSuite) -> None:
    with pytest.raises(ValueError):
        cipher_suite.normalize(op="sign", alg="ES256")


@pytest.mark.unit
def test_normalize_rejects_unsupported_operation(
    cipher_suite: Fips205CipherSuite,
) -> None:
    with pytest.raises(ValueError):
        cipher_suite.normalize(op="encrypt")
