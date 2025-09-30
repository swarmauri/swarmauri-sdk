"""Unit tests for :mod:`swarmauri_cipher_suite_webauthn` components."""

import pytest

from swarmauri_cipher_suite_webauthn import WebAuthnCipherSuite


@pytest.fixture
def cipher_suite() -> WebAuthnCipherSuite:
    return WebAuthnCipherSuite()


# Standard component tests
@pytest.mark.unit
def test_ubc_resource(cipher_suite: WebAuthnCipherSuite) -> None:
    assert cipher_suite.resource == "CipherSuite"


@pytest.mark.unit
def test_ubc_type(cipher_suite: WebAuthnCipherSuite) -> None:
    assert cipher_suite.type == "WebAuthnCipherSuite"


@pytest.mark.unit
def test_initialization(cipher_suite: WebAuthnCipherSuite) -> None:
    assert isinstance(cipher_suite.id, str)


@pytest.mark.unit
def test_serialization(cipher_suite: WebAuthnCipherSuite) -> None:
    restored = WebAuthnCipherSuite.model_validate_json(cipher_suite.model_dump_json())
    assert restored.id == cipher_suite.id


@pytest.mark.unit
def test_suite_identifier(cipher_suite: WebAuthnCipherSuite) -> None:
    assert cipher_suite.suite_id() == "webauthn"


# Cipher-suite specific behavior
@pytest.mark.unit
def test_supports_expected_algorithms(cipher_suite: WebAuthnCipherSuite) -> None:
    supports = cipher_suite.supports()
    assert set(supports.keys()) == {"sign", "verify"}
    assert set(supports["sign"]) == {"-7", "-8", "-257"}
    assert supports["sign"] == supports["verify"]


@pytest.mark.unit
@pytest.mark.parametrize("operation", ["sign", "verify"])
def test_default_alg(cipher_suite: WebAuthnCipherSuite, operation: str) -> None:
    assert cipher_suite.default_alg(operation) == "-7"


@pytest.mark.unit
def test_features_descriptor(cipher_suite: WebAuthnCipherSuite) -> None:
    features = cipher_suite.features()
    assert features["suite"] == "webauthn"
    assert features["version"] == 1
    assert features["ops"]["sign"]["default"] == "-7"
    assert set(features["ops"]["sign"]["allowed"]) == {"-7", "-8", "-257"}
    assert set(features["dialects"]["cose"]) == {"-7", "-8", "-257"}
    assert set(features["dialects"]["fido2"]) == {"-7", "-8", "-257"}
    assert features["constraints"]["attestation_formats"] == [
        "packed",
        "tpm",
        "android-safetynet",
        "apple",
    ]
    assert features["compliance"] == {"fips": False}


@pytest.mark.unit
def test_normalize_coerces_alg_to_string(cipher_suite: WebAuthnCipherSuite) -> None:
    descriptor = cipher_suite.normalize(op="sign", alg=-8)

    assert descriptor["op"] == "sign"
    assert descriptor["alg"] == "-8"
    assert descriptor["dialect"] == "cose"


@pytest.mark.unit
def test_normalize_maps_cose_identifier(cipher_suite: WebAuthnCipherSuite) -> None:
    descriptor = cipher_suite.normalize(op="sign", alg="-7")

    assert descriptor["mapped"] == {"cose": -7, "fido2": "-7", "provider": "-7"}


@pytest.mark.unit
def test_normalize_preserves_params(cipher_suite: WebAuthnCipherSuite) -> None:
    params = {"userVerification": "preferred"}
    descriptor = cipher_suite.normalize(op="sign", alg="-257", params=params)

    assert descriptor["params"] == params
    assert descriptor["params"] is not params
    assert descriptor["policy"] == {}


@pytest.mark.unit
def test_normalize_raises_for_unsupported_alg(
    cipher_suite: WebAuthnCipherSuite,
) -> None:
    with pytest.raises(ValueError):
        cipher_suite.normalize(op="sign", alg="ES256")
