import pytest

from swarmauri_cipher_suite_tls13 import Tls13CipherSuite


@pytest.fixture
def cipher_suite() -> Tls13CipherSuite:
    return Tls13CipherSuite()


# Standard component tests
@pytest.mark.unit
def test_ubc_resource(cipher_suite: Tls13CipherSuite) -> None:
    assert cipher_suite.resource == "CipherSuite"


@pytest.mark.unit
def test_ubc_type(cipher_suite: Tls13CipherSuite) -> None:
    assert cipher_suite.type == "Tls13CipherSuite"


@pytest.mark.unit
def test_initialization(cipher_suite: Tls13CipherSuite) -> None:
    assert isinstance(cipher_suite.id, str)


@pytest.mark.unit
def test_serialization(cipher_suite: Tls13CipherSuite) -> None:
    restored = Tls13CipherSuite.model_validate_json(cipher_suite.model_dump_json())
    assert restored.id == cipher_suite.id


@pytest.mark.unit
def test_suite_identifier(cipher_suite: Tls13CipherSuite) -> None:
    assert cipher_suite.suite_id() == "tls13"


# Cipher-suite specific behavior
@pytest.mark.unit
def test_supports_expected_algorithms(cipher_suite: Tls13CipherSuite) -> None:
    supports = cipher_suite.supports()
    assert set(supports.keys()) == {"encrypt", "decrypt"}
    expected = {
        "TLS_AES_128_GCM_SHA256",
        "TLS_AES_256_GCM_SHA384",
        "TLS_CHACHA20_POLY1305_SHA256",
    }
    for operation in ("encrypt", "decrypt"):
        assert set(supports[operation]) == expected


@pytest.mark.unit
@pytest.mark.parametrize("operation", ["encrypt", "decrypt"])
def test_default_alg(cipher_suite: Tls13CipherSuite, operation: str) -> None:
    assert cipher_suite.default_alg(operation) == "TLS_AES_256_GCM_SHA384"


@pytest.mark.unit
def test_features_descriptor(cipher_suite: Tls13CipherSuite) -> None:
    features = cipher_suite.features()
    assert features["suite"] == "tls13"
    assert features["version"] == 1
    assert features["ops"]["encrypt"]["default"] == "TLS_AES_256_GCM_SHA384"
    assert features["ops"]["encrypt"]["allowed"] == [
        "TLS_AES_128_GCM_SHA256",
        "TLS_AES_256_GCM_SHA384",
        "TLS_CHACHA20_POLY1305_SHA256",
    ]
    assert features["constraints"]["record_max"] == 16384
    assert features["constraints"]["aead"] == {"tagBits": 128}


@pytest.mark.unit
def test_normalize_with_explicit_alg(cipher_suite: Tls13CipherSuite) -> None:
    descriptor = cipher_suite.normalize(
        op="encrypt",
        alg="TLS_AES_128_GCM_SHA256",
        params={"padding": None},
    )

    assert descriptor["op"] == "encrypt"
    assert descriptor["alg"] == "TLS_AES_128_GCM_SHA256"
    assert descriptor["dialect"] == "tls"
    assert descriptor["mapped"] == {
        "tls": "TLS_AES_128_GCM_SHA256",
        "provider": "TLS_AES_128_GCM_SHA256",
    }
    assert descriptor["params"] == {"padding": None}
    assert descriptor["constraints"] == {"record_max": 16384, "tagBits": 128}
    assert descriptor["policy"] == cipher_suite.policy()


@pytest.mark.unit
def test_normalize_defaults(cipher_suite: Tls13CipherSuite) -> None:
    descriptor = cipher_suite.normalize(op="decrypt")

    assert descriptor["alg"] == "TLS_AES_256_GCM_SHA384"
    assert descriptor["dialect"] == "tls"
    assert descriptor["mapped"] == {
        "tls": "TLS_AES_256_GCM_SHA384",
        "provider": "TLS_AES_256_GCM_SHA384",
    }
    assert descriptor["params"] == {}


@pytest.mark.unit
def test_normalize_rejects_unsupported_alg(cipher_suite: Tls13CipherSuite) -> None:
    with pytest.raises(ValueError):
        cipher_suite.normalize(op="encrypt", alg="TLS_AES_128_CCM_SHA256")
