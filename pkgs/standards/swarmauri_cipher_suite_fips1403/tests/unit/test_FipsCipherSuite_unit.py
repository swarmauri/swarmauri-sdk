import pytest

from swarmauri_cipher_suite_fips1403 import FipsCipherSuite


@pytest.fixture
def cipher_suite() -> FipsCipherSuite:
    return FipsCipherSuite()


# Standard component tests
@pytest.mark.unit
def test_ubc_resource(cipher_suite: FipsCipherSuite) -> None:
    assert cipher_suite.resource == "CipherSuite"


@pytest.mark.unit
def test_ubc_type(cipher_suite: FipsCipherSuite) -> None:
    assert cipher_suite.type == "FipsCipherSuite"


@pytest.mark.unit
def test_initialization(cipher_suite: FipsCipherSuite) -> None:
    assert isinstance(cipher_suite.id, str)


@pytest.mark.unit
def test_serialization(cipher_suite: FipsCipherSuite) -> None:
    restored = FipsCipherSuite.model_validate_json(cipher_suite.model_dump_json())
    assert restored.id == cipher_suite.id


@pytest.mark.unit
def test_suite_identifier(cipher_suite: FipsCipherSuite) -> None:
    assert cipher_suite.suite_id() == "fips140-3"


# Cipher-suite specific behavior
@pytest.mark.unit
def test_supports_expected_algorithms(cipher_suite: FipsCipherSuite) -> None:
    supports = cipher_suite.supports()
    assert set(supports.keys()) == {
        "sign",
        "verify",
        "encrypt",
        "decrypt",
        "wrap",
        "unwrap",
    }
    assert tuple(supports["sign"]) == ("PS256", "PS384", "ES256", "ES384")
    assert supports["sign"] == supports["verify"]
    assert tuple(supports["encrypt"]) == ("A256GCM",)
    assert supports["encrypt"] == supports["decrypt"]
    assert tuple(supports["wrap"]) == ("RSA-OAEP-256", "A256KW")
    assert supports["wrap"] == supports["unwrap"]


@pytest.mark.unit
@pytest.mark.parametrize(
    ("operation", "expected"),
    [
        ("sign", "PS256"),
        ("encrypt", "A256GCM"),
        ("wrap", "RSA-OAEP-256"),
        ("decrypt", "A256GCM"),
        ("verify", "A256GCM"),
        ("unwrap", "A256GCM"),
    ],
)
def test_default_alg(
    cipher_suite: FipsCipherSuite, operation: str, expected: str
) -> None:
    assert cipher_suite.default_alg(operation) == expected


@pytest.mark.unit
def test_features_descriptor(cipher_suite: FipsCipherSuite) -> None:
    features = cipher_suite.features()
    policy = cipher_suite.policy()

    assert features["suite"] == "fips140-3"
    assert features["version"] == 1
    assert set(features["dialects"]["jwa"]) == {
        "PS256",
        "PS384",
        "ES256",
        "ES384",
        "A256GCM",
        "RSA-OAEP-256",
        "A256KW",
    }
    assert features["ops"]["sign"]["default"] == "PS256"
    assert features["ops"]["encrypt"]["default"] == "A256GCM"
    assert features["ops"]["wrap"]["default"] == "RSA-OAEP-256"
    assert features["constraints"]["min_rsa_bits"] == policy["min_rsa_bits"]
    assert features["constraints"]["allowed_curves"] == list(policy["allowed_curves"])
    assert features["constraints"]["aead"]["tagBits"] == policy["aead_tag_bits"]
    assert features["compliance"]["fips"] is policy["fips"]


@pytest.mark.unit
def test_policy_exposes_expected_metadata(cipher_suite: FipsCipherSuite) -> None:
    policy = cipher_suite.policy()

    assert policy["fips"] is True
    assert policy["min_rsa_bits"] == 2048
    assert policy["allowed_curves"] == ("P-256", "P-384")
    assert policy["hashes"] == ("SHA256", "SHA384")
    assert policy["aead_tag_bits"] == 128


@pytest.mark.unit
def test_normalize_with_explicit_alg(cipher_suite: FipsCipherSuite) -> None:
    descriptor = cipher_suite.normalize(
        op="sign",
        alg="ES256",
        params={"detached": True},
    )

    assert descriptor["op"] == "sign"
    assert descriptor["alg"] == "ES256"
    assert descriptor["dialect"] == "jwa"
    assert descriptor["mapped"] == {"jwa": "ES256", "provider": "ES256"}
    assert descriptor["params"] == {"detached": True, "hash": "SHA256"}
    assert descriptor["constraints"] == {
        "minKeyBits": 2048,
        "curves": ("P-256", "P-384"),
        "hashes": ("SHA256", "SHA384"),
    }
    assert descriptor["policy"] == cipher_suite.policy()


@pytest.mark.unit
def test_normalize_applies_aead_defaults(cipher_suite: FipsCipherSuite) -> None:
    descriptor = cipher_suite.normalize(op="encrypt")

    assert descriptor["alg"] == "A256GCM"
    assert descriptor["params"]["tagBits"] == 128
    assert descriptor["params"]["nonceLen"] == 12


@pytest.mark.unit
def test_normalize_derives_rsa_pss_defaults(cipher_suite: FipsCipherSuite) -> None:
    descriptor = cipher_suite.normalize(op="sign", alg="PS384")

    assert descriptor["params"]["saltBits"] == 384
    assert descriptor["params"]["hash"] == "SHA384"


@pytest.mark.unit
def test_normalize_derives_ecdsa_defaults(cipher_suite: FipsCipherSuite) -> None:
    descriptor = cipher_suite.normalize(op="sign", alg="ES384")

    assert descriptor["params"]["hash"] == "SHA384"


@pytest.mark.unit
def test_normalize_rejects_unsupported_alg(cipher_suite: FipsCipherSuite) -> None:
    with pytest.raises(ValueError):
        cipher_suite.normalize(op="sign", alg="HS256")
