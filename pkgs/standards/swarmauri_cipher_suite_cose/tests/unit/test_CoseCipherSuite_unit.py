import pytest

from swarmauri_cipher_suite_cose import CoseCipherSuite


@pytest.fixture
def cipher_suite() -> CoseCipherSuite:
    return CoseCipherSuite()


# Standard component tests
@pytest.mark.unit
def test_ubc_resource(cipher_suite: CoseCipherSuite) -> None:
    assert cipher_suite.resource == "CipherSuite"


@pytest.mark.unit
def test_ubc_type(cipher_suite: CoseCipherSuite) -> None:
    assert cipher_suite.type == "CoseCipherSuite"


@pytest.mark.unit
def test_initialization(cipher_suite: CoseCipherSuite) -> None:
    assert isinstance(cipher_suite.id, str)


@pytest.mark.unit
def test_serialization(cipher_suite: CoseCipherSuite) -> None:
    restored = CoseCipherSuite.model_validate_json(cipher_suite.model_dump_json())
    assert restored.id == cipher_suite.id


@pytest.mark.unit
def test_suite_identifier(cipher_suite: CoseCipherSuite) -> None:
    assert cipher_suite.suite_id() == "cose"


# Cipher-suite specific behavior
@pytest.mark.unit
def test_supports_expected_algorithms(cipher_suite: CoseCipherSuite) -> None:
    supports = cipher_suite.supports()

    assert set(supports.keys()) == {"sign", "verify", "encrypt", "decrypt"}
    assert supports["sign"] == supports["verify"]
    assert set(supports["sign"]) == {"-8", "-7", "-35", "-36", "-37", "-38", "-39"}
    assert set(supports["encrypt"]) == {"1", "2", "3"}
    assert supports["encrypt"] == supports["decrypt"]


@pytest.mark.unit
@pytest.mark.parametrize(
    "operation",
    ["sign", "encrypt", "decrypt"],
)
def test_default_alg(cipher_suite: CoseCipherSuite, operation: str) -> None:
    expected = "-8" if operation == "sign" else "3"
    assert cipher_suite.default_alg(operation) == expected


@pytest.mark.unit
def test_features_descriptor(cipher_suite: CoseCipherSuite) -> None:
    features = cipher_suite.features()

    assert features["suite"] == "cose"
    assert features["version"] == 1
    assert set(features["dialects"]["cose"]) == {
        "-8",
        "-7",
        "-35",
        "-36",
        "-37",
        "-38",
        "-39",
        "1",
        "2",
        "3",
    }
    assert features["ops"]["sign"]["default"] == "-8"
    assert features["ops"]["encrypt"]["default"] == "3"
    assert features["constraints"]["aead"] == {"tagBits": 128, "nonceLen": 12}


@pytest.mark.unit
def test_normalize_with_string_coercion(cipher_suite: CoseCipherSuite) -> None:
    descriptor = cipher_suite.normalize(op="sign", alg=-7)

    assert descriptor["alg"] == "-7"
    assert descriptor["mapped"] == {"cose": -7, "provider": "-7"}
    assert descriptor["dialect"] == "cose"


@pytest.mark.unit
def test_normalize_applies_aead_defaults(cipher_suite: CoseCipherSuite) -> None:
    descriptor = cipher_suite.normalize(op="encrypt", alg=1, params={})

    assert descriptor["alg"] == "1"
    assert descriptor["mapped"] == {"cose": 1, "provider": "1"}
    assert descriptor["params"] == {"tagBits": 128, "nonceLen": 12}


@pytest.mark.unit
def test_normalize_uses_defaults_when_alg_missing(
    cipher_suite: CoseCipherSuite,
) -> None:
    descriptor = cipher_suite.normalize(op="decrypt")

    assert descriptor["alg"] == "3"
    assert descriptor["mapped"] == {"cose": 3, "provider": "3"}
    assert descriptor["params"] == {"tagBits": 128, "nonceLen": 12}


@pytest.mark.unit
def test_normalize_rejects_unsupported_alg(cipher_suite: CoseCipherSuite) -> None:
    with pytest.raises(ValueError):
        cipher_suite.normalize(op="sign", alg="999")
