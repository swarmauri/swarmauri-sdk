import pytest

from swarmauri_cipher_suite_sigstore import SigstoreCipherSuite


@pytest.fixture
def cipher_suite() -> SigstoreCipherSuite:
    return SigstoreCipherSuite()


# Standard component tests
@pytest.mark.unit
def test_ubc_resource(cipher_suite: SigstoreCipherSuite) -> None:
    assert cipher_suite.resource == "CipherSuite"


@pytest.mark.unit
def test_ubc_type(cipher_suite: SigstoreCipherSuite) -> None:
    assert cipher_suite.type == "SigstoreCipherSuite"


@pytest.mark.unit
def test_initialization(cipher_suite: SigstoreCipherSuite) -> None:
    assert isinstance(cipher_suite.id, str)


@pytest.mark.unit
def test_serialization(cipher_suite: SigstoreCipherSuite) -> None:
    restored = SigstoreCipherSuite.model_validate_json(cipher_suite.model_dump_json())
    assert restored.id == cipher_suite.id


@pytest.mark.unit
def test_suite_identifier(cipher_suite: SigstoreCipherSuite) -> None:
    assert cipher_suite.suite_id() == "sigstore"


# Cipher-suite specific behavior
@pytest.mark.unit
def test_supports_expected_algorithms(cipher_suite: SigstoreCipherSuite) -> None:
    supports = cipher_suite.supports()
    assert set(supports.keys()) == {"sign", "verify"}
    assert set(supports["sign"]) == {"ES256", "EdDSA", "PS256"}
    assert supports["sign"] == supports["verify"]


@pytest.mark.unit
@pytest.mark.parametrize("operation", ["sign", "verify"])
def test_default_alg(cipher_suite: SigstoreCipherSuite, operation: str) -> None:
    assert cipher_suite.default_alg(operation) == "ES256"


@pytest.mark.unit
def test_features_descriptor(cipher_suite: SigstoreCipherSuite) -> None:
    features = cipher_suite.features()
    assert features["suite"] == "sigstore"
    assert features["version"] == 1
    assert features["dialects"]["sigstore"] == ["rekor", "tsa:rfc3161"]
    assert features["constraints"]["tsa"] == {"required": False}
    assert features["notes"] == ["Cosign-style transparency log + optional TSA"]


@pytest.mark.unit
def test_normalize_dual_dialect_mapping(cipher_suite: SigstoreCipherSuite) -> None:
    descriptor = cipher_suite.normalize(op="sign", alg="EdDSA", params={"bundle": True})

    assert descriptor["alg"] == "EdDSA"
    assert descriptor["dialect"] == "jwa"
    assert descriptor["mapped"] == {
        "jwa": "EdDSA",
        "sigstore": "EdDSA",
        "provider": "EdDSA",
    }


@pytest.mark.unit
def test_normalize_param_passthrough_and_policy(
    cipher_suite: SigstoreCipherSuite,
) -> None:
    params = {"bundle": True, "upload": False}
    descriptor = cipher_suite.normalize(
        op="sign", alg="PS256", params=params, dialect="sigstore"
    )

    assert descriptor["dialect"] == "sigstore"
    assert descriptor["params"] == params
    assert descriptor["constraints"] == {}
    assert descriptor["policy"] == cipher_suite.policy()


@pytest.mark.unit
def test_normalize_invalid_algorithm(cipher_suite: SigstoreCipherSuite) -> None:
    with pytest.raises(ValueError):
        cipher_suite.normalize(op="sign", alg="RSA-PSS-SHA256")
