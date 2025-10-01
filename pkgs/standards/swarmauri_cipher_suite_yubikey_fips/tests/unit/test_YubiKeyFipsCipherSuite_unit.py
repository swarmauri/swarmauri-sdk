import pytest

from swarmauri_cipher_suite_yubikey_fips import YubiKeyFipsCipherSuite


@pytest.fixture
def cipher_suite() -> YubiKeyFipsCipherSuite:
    return YubiKeyFipsCipherSuite()


# Standard component tests
@pytest.mark.unit
def test_ubc_resource(cipher_suite: YubiKeyFipsCipherSuite) -> None:
    assert cipher_suite.resource == "CipherSuite"


@pytest.mark.unit
def test_ubc_type(cipher_suite: YubiKeyFipsCipherSuite) -> None:
    assert cipher_suite.type == "YubiKeyFipsCipherSuite"


@pytest.mark.unit
def test_initialization(cipher_suite: YubiKeyFipsCipherSuite) -> None:
    assert isinstance(cipher_suite.id, str)


@pytest.mark.unit
def test_serialization(cipher_suite: YubiKeyFipsCipherSuite) -> None:
    restored = YubiKeyFipsCipherSuite.model_validate_json(
        cipher_suite.model_dump_json()
    )
    assert restored.id == cipher_suite.id


@pytest.mark.unit
def test_suite_identifier(cipher_suite: YubiKeyFipsCipherSuite) -> None:
    assert cipher_suite.suite_id() == "yubikey-fips"


# Cipher-suite specific behavior
@pytest.mark.unit
def test_supports_expected_algorithms(cipher_suite: YubiKeyFipsCipherSuite) -> None:
    supports = cipher_suite.supports()
    assert set(supports.keys()) == {"sign", "verify", "wrap", "unwrap"}
    assert tuple(supports["sign"]) == ("PS256", "PS384", "ES256", "ES384")
    assert supports["verify"] == supports["sign"]
    assert tuple(supports["wrap"]) == ("RSA-OAEP-256",)
    assert supports["unwrap"] == supports["wrap"]


@pytest.mark.unit
@pytest.mark.parametrize("operation", ["sign", "wrap"])
def test_default_alg(cipher_suite: YubiKeyFipsCipherSuite, operation: str) -> None:
    expected = "PS256" if operation == "sign" else "RSA-OAEP-256"
    assert cipher_suite.default_alg(operation) == expected


@pytest.mark.unit
def test_features_descriptor(cipher_suite: YubiKeyFipsCipherSuite) -> None:
    features = cipher_suite.features()
    assert features["suite"] == "yubikey-fips"
    assert features["version"] == 1
    assert features["ops"]["sign"]["default"] == "PS256"
    assert set(features["ops"]["sign"]["allowed"]) == {
        "PS256",
        "PS384",
        "ES256",
        "ES384",
    }
    assert features["ops"]["wrap"]["default"] == "RSA-OAEP-256"
    assert features["dialects"]["provider"] == ["piv"]
    assert features["constraints"]["rsa_pss"] == {
        "mgf1": "hash-match",
        "saltLen": "hashLen",
    }
    assert features["compliance"] == {"fips": True}


@pytest.mark.unit
def test_normalize_ps256_defaults(cipher_suite: YubiKeyFipsCipherSuite) -> None:
    descriptor = cipher_suite.normalize(op="sign", alg="PS256")

    assert descriptor["dialect"] == "jwa"
    assert descriptor["mapped"] == {"jwa": "PS256", "provider": "piv:PS256"}
    assert descriptor["params"]["saltLen"] == 32
    assert descriptor["params"]["mgf1Hash"] == "SHA256"


@pytest.mark.unit
def test_normalize_es384_hash_default(cipher_suite: YubiKeyFipsCipherSuite) -> None:
    descriptor = cipher_suite.normalize(op="sign", alg="ES384")

    assert descriptor["params"]["hash"] == "SHA384"


@pytest.mark.unit
def test_normalize_provider_slot(cipher_suite: YubiKeyFipsCipherSuite) -> None:
    descriptor = cipher_suite.normalize(
        op="sign",
        alg="PS256",
        key={"slot": "9c"},
    )

    assert descriptor["mapped"]["provider"] == "piv:PS256:slot=9c"


@pytest.mark.unit
def test_normalize_constraints_and_policy(cipher_suite: YubiKeyFipsCipherSuite) -> None:
    descriptor = cipher_suite.normalize(op="sign", alg="PS256")

    assert descriptor["constraints"] == {
        "minKeyBits": 2048,
        "curves": ("P-256", "P-384"),
    }
    assert descriptor["policy"] == cipher_suite.policy()


@pytest.mark.unit
def test_normalize_unsupported_algorithm(cipher_suite: YubiKeyFipsCipherSuite) -> None:
    with pytest.raises(ValueError):
        cipher_suite.normalize(op="sign", alg="EdDSA")
