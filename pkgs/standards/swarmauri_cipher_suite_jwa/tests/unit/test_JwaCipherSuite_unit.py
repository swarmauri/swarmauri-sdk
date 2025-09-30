import pytest

from swarmauri_cipher_suite_jwa import JwaCipherSuite


@pytest.fixture
def cipher_suite() -> JwaCipherSuite:
    return JwaCipherSuite()


# Standard component tests
@pytest.mark.unit
def test_ubc_resource(cipher_suite: JwaCipherSuite) -> None:
    assert cipher_suite.resource == "CipherSuite"


@pytest.mark.unit
def test_ubc_type(cipher_suite: JwaCipherSuite) -> None:
    assert cipher_suite.type == "JwaCipherSuite"


@pytest.mark.unit
def test_initialization(cipher_suite: JwaCipherSuite) -> None:
    assert isinstance(cipher_suite.id, str)


@pytest.mark.unit
def test_serialization(cipher_suite: JwaCipherSuite) -> None:
    restored = JwaCipherSuite.model_validate_json(cipher_suite.model_dump_json())
    assert restored.id == cipher_suite.id


@pytest.mark.unit
def test_suite_identifier(cipher_suite: JwaCipherSuite) -> None:
    assert cipher_suite.suite_id() == "jwa"


# Cipher-suite specific behavior
@pytest.mark.unit
def test_supports_expected_algorithms(cipher_suite: JwaCipherSuite) -> None:
    supports = cipher_suite.supports()
    assert supports == {
        "sign": ("EdDSA", "PS256", "PS384", "PS512", "ES256", "ES384", "ES512"),
        "verify": ("EdDSA", "PS256", "PS384", "PS512", "ES256", "ES384", "ES512"),
        "encrypt": ("A128GCM", "A192GCM", "A256GCM"),
        "decrypt": ("A128GCM", "A192GCM", "A256GCM"),
        "wrap": ("RSA-OAEP", "RSA-OAEP-256", "A256KW"),
        "unwrap": ("RSA-OAEP", "RSA-OAEP-256", "A256KW"),
    }


@pytest.mark.unit
@pytest.mark.parametrize(
    ("operation", "expected"),
    [
        ("sign", "EdDSA"),
        ("verify", "A256GCM"),
        ("encrypt", "A256GCM"),
        ("decrypt", "A256GCM"),
        ("wrap", "RSA-OAEP-256"),
        ("unwrap", "A256GCM"),
    ],
)
def test_default_alg(
    cipher_suite: JwaCipherSuite, operation: str, expected: str
) -> None:
    assert cipher_suite.default_alg(operation) == expected


@pytest.mark.unit
def test_features_descriptor(cipher_suite: JwaCipherSuite) -> None:
    features = cipher_suite.features()

    assert features["suite"] == "jwa"
    assert features["version"] == 1
    assert features["constraints"] == {"aead": {"tagBits": 128, "nonceLen": 12}}

    expected_jwa = sorted(
        {
            "EdDSA",
            "PS256",
            "PS384",
            "PS512",
            "ES256",
            "ES384",
            "ES512",
            "A128GCM",
            "A192GCM",
            "A256GCM",
            "RSA-OAEP",
            "RSA-OAEP-256",
            "A256KW",
        }
    )
    assert features["dialects"]["jwa"] == expected_jwa

    expected_cose = sorted([-8, -7, -35, -36, -37, -38, -39, 1, 2, 3])
    assert sorted(features["dialects"]["cose"]) == expected_cose

    for operation, expected in [
        ("sign", "EdDSA"),
        ("verify", "A256GCM"),
        ("encrypt", "A256GCM"),
        ("decrypt", "A256GCM"),
        ("wrap", "RSA-OAEP-256"),
        ("unwrap", "A256GCM"),
    ]:
        assert features["ops"][operation]["default"] == expected


@pytest.mark.unit
def test_normalize_mapping_with_cose_id(cipher_suite: JwaCipherSuite) -> None:
    descriptor = cipher_suite.normalize(op="sign", alg="ES256")

    assert descriptor["op"] == "sign"
    assert descriptor["alg"] == "ES256"
    assert descriptor["dialect"] == "jwa"
    assert descriptor["mapped"] == {"jwa": "ES256", "cose": -7, "provider": "ES256"}
    assert descriptor["constraints"] == {"minKeyBits": 0}
    assert descriptor["policy"] == {}


@pytest.mark.unit
def test_normalize_applies_aead_defaults(cipher_suite: JwaCipherSuite) -> None:
    descriptor = cipher_suite.normalize(op="encrypt", alg="A128GCM")

    assert descriptor["params"]["tagBits"] == 128
    assert descriptor["params"]["nonceLen"] == 12
    assert descriptor["mapped"]["cose"] == 1


@pytest.mark.unit
def test_normalize_derives_rsapss_saltbits(cipher_suite: JwaCipherSuite) -> None:
    descriptor = cipher_suite.normalize(op="sign", alg="PS512")

    assert descriptor["params"]["saltBits"] == 512


@pytest.mark.unit
def test_normalize_rejects_unsupported_alg(cipher_suite: JwaCipherSuite) -> None:
    with pytest.raises(ValueError):
        cipher_suite.normalize(op="sign", alg="HS256")
