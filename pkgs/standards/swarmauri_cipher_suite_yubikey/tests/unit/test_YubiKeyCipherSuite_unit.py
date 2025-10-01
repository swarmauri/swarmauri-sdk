import pytest

from swarmauri_cipher_suite_yubikey import YubiKeyCipherSuite


@pytest.fixture
def cipher_suite() -> YubiKeyCipherSuite:
    return YubiKeyCipherSuite()


# Standard component tests
@pytest.mark.unit
def test_ubc_resource(cipher_suite: YubiKeyCipherSuite) -> None:
    assert cipher_suite.resource == "CipherSuite"


@pytest.mark.unit
def test_ubc_type(cipher_suite: YubiKeyCipherSuite) -> None:
    assert cipher_suite.type == "YubiKeyCipherSuite"


@pytest.mark.unit
def test_initialization(cipher_suite: YubiKeyCipherSuite) -> None:
    assert isinstance(cipher_suite.id, str)


@pytest.mark.unit
def test_serialization(cipher_suite: YubiKeyCipherSuite) -> None:
    restored = YubiKeyCipherSuite.model_validate_json(cipher_suite.model_dump_json())
    assert restored.id == cipher_suite.id


@pytest.mark.unit
def test_suite_identifier(cipher_suite: YubiKeyCipherSuite) -> None:
    assert cipher_suite.suite_id() == "yubikey"


# Cipher-suite specific behavior
@pytest.mark.unit
def test_supports_expected_algorithms(cipher_suite: YubiKeyCipherSuite) -> None:
    supports = cipher_suite.supports()
    assert set(supports.keys()) == {"sign", "verify", "wrap", "unwrap"}
    assert set(supports["sign"]) == {"PS256", "PS384", "PS512", "ES256", "ES384", "EdDSA"}
    assert supports["sign"] == supports["verify"]
    assert supports["wrap"] == supports["unwrap"]


@pytest.mark.unit
@pytest.mark.parametrize(
    ("operation", "expected"),
    [
        ("sign", "ES256"),
        ("verify", "ES256"),
        ("wrap", "RSA-OAEP-256"),
        ("unwrap", "ES256"),
    ],
)
def test_default_alg(cipher_suite: YubiKeyCipherSuite, operation: str, expected: str) -> None:
    assert cipher_suite.default_alg(operation) == expected


@pytest.mark.unit
def test_features_descriptor(cipher_suite: YubiKeyCipherSuite) -> None:
    features = cipher_suite.features()
    supports = cipher_suite.supports()

    assert features["suite"] == "yubikey"
    assert features["version"] == 1
    assert set(features["dialects"]["jwa"]) == set({*supports["sign"], *supports["wrap"]})
    assert features["dialects"]["provider"] == ["piv"]
    assert features["ops"]["sign"]["default"] == "ES256"
    assert features["ops"]["wrap"]["default"] == "RSA-OAEP-256"
    assert features["constraints"] == {
        "min_rsa_bits": 2048,
        "allowed_curves": ["P-256", "P-384"],
        "rsa_pss": {"mgf1": "hash-match", "saltLen": "hashLen"},
    }
    assert features["notes"] == [
        "PIV-backed signing/unwrap; EdDSA allowed on non-FIPS models/firmware.",
    ]


@pytest.mark.unit
def test_normalize_rsapss_defaults(cipher_suite: YubiKeyCipherSuite) -> None:
    descriptor = cipher_suite.normalize(op="sign", alg="PS256")

    assert descriptor["alg"] == "PS256"
    assert descriptor["params"]["saltLen"] == 32
    assert descriptor["params"]["mgf1Hash"] == "SHA256"


@pytest.mark.unit
def test_normalize_ecdsa_defaults(cipher_suite: YubiKeyCipherSuite) -> None:
    descriptor = cipher_suite.normalize(op="sign", alg="ES256")

    assert descriptor["alg"] == "ES256"
    assert descriptor["params"]["hash"] == "SHA256"


@pytest.mark.unit
def test_normalize_provider_mapping_without_slot(cipher_suite: YubiKeyCipherSuite) -> None:
    descriptor = cipher_suite.normalize(op="wrap", alg="RSA-OAEP-256")

    assert descriptor["mapped"]["provider"] == "piv:RSA-OAEP-256"


@pytest.mark.unit
def test_normalize_provider_mapping_with_slot(cipher_suite: YubiKeyCipherSuite) -> None:
    descriptor = cipher_suite.normalize(op="sign", alg="ES384", key={"slot": "9a"})

    assert descriptor["mapped"]["provider"] == "piv:ES384:slot=9a"


@pytest.mark.unit
def test_normalize_constraints(cipher_suite: YubiKeyCipherSuite) -> None:
    descriptor = cipher_suite.normalize(op="sign")

    assert descriptor["constraints"] == {"minKeyBits": 2048, "curves": ("P-256", "P-384")}


@pytest.mark.unit
def test_normalize_rejects_unsupported_alg(cipher_suite: YubiKeyCipherSuite) -> None:
    with pytest.raises(ValueError):
        cipher_suite.normalize(op="sign", alg="RS256")
