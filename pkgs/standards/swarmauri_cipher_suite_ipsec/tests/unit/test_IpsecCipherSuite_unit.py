import pytest

from swarmauri_cipher_suite_ipsec import IpsecCipherSuite


@pytest.fixture
def cipher_suite() -> IpsecCipherSuite:
    return IpsecCipherSuite()


# Standard component tests
@pytest.mark.unit
def test_ubc_resource(cipher_suite: IpsecCipherSuite) -> None:
    assert cipher_suite.resource == "CipherSuite"


@pytest.mark.unit
def test_ubc_type(cipher_suite: IpsecCipherSuite) -> None:
    assert cipher_suite.type == "IpsecCipherSuite"


@pytest.mark.unit
def test_initialization(cipher_suite: IpsecCipherSuite) -> None:
    assert isinstance(cipher_suite.id, str)


@pytest.mark.unit
def test_serialization(cipher_suite: IpsecCipherSuite) -> None:
    restored = IpsecCipherSuite.model_validate_json(cipher_suite.model_dump_json())
    assert restored.id == cipher_suite.id


@pytest.mark.unit
def test_suite_identifier(cipher_suite: IpsecCipherSuite) -> None:
    assert cipher_suite.suite_id() == "ipsec"


# Cipher-suite specific behavior
@pytest.mark.unit
def test_supports_expected_algorithms(cipher_suite: IpsecCipherSuite) -> None:
    supports = cipher_suite.supports()
    assert set(supports.keys()) == {"encrypt", "decrypt"}
    assert set(supports["encrypt"]) == {"AES-GCM-16", "CHACHA20-POLY1305"}
    assert supports["encrypt"] == supports["decrypt"]


@pytest.mark.unit
@pytest.mark.parametrize("operation", ["encrypt", "decrypt"])
def test_default_alg(cipher_suite: IpsecCipherSuite, operation: str) -> None:
    assert cipher_suite.default_alg(operation) == "AES-GCM-16"


@pytest.mark.unit
def test_features_descriptor(cipher_suite: IpsecCipherSuite) -> None:
    features = cipher_suite.features()
    assert features["suite"] == "ipsec"
    assert features["version"] == 1
    assert features["ops"]["encrypt"]["default"] == "AES-GCM-16"
    assert set(features["ops"]["encrypt"]["allowed"]) == {
        "AES-GCM-16",
        "CHACHA20-POLY1305",
    }
    assert set(features["dialects"]["ike"]) == {"AES-GCM-16", "CHACHA20-POLY1305"}
    assert tuple(features["constraints"]["prf"]) == ("HMAC-SHA2-256", "HMAC-SHA2-384")
    assert tuple(features["constraints"]["dh"]) == (
        "group14",
        "group19",
        "group20",
        "group31",
    )
    assert features["constraints"]["pfs"] is True
    assert features["compliance"]["fips"] is False


@pytest.mark.unit
def test_normalize_with_explicit_alg(cipher_suite: IpsecCipherSuite) -> None:
    descriptor = cipher_suite.normalize(
        op="encrypt",
        alg="CHACHA20-POLY1305",
        params={"lifetime": 3600},
    )

    assert descriptor["op"] == "encrypt"
    assert descriptor["alg"] == "CHACHA20-POLY1305"
    assert descriptor["dialect"] == "ike"
    assert descriptor["mapped"] == {
        "ike": "CHACHA20-POLY1305",
        "provider": "CHACHA20-POLY1305",
    }
    assert descriptor["params"] == {"lifetime": 3600}
    assert descriptor["constraints"] == {}
    assert descriptor["policy"] == {}


@pytest.mark.unit
def test_normalize_rejects_unsupported_alg(cipher_suite: IpsecCipherSuite) -> None:
    with pytest.raises(ValueError):
        cipher_suite.normalize(op="encrypt", alg="AES-GCM-8")


@pytest.mark.unit
def test_normalize_defaults(cipher_suite: IpsecCipherSuite) -> None:
    descriptor = cipher_suite.normalize(op="decrypt")

    assert descriptor["alg"] == "AES-GCM-16"
    assert descriptor["dialect"] == "ike"
    assert descriptor["mapped"] == {
        "ike": "AES-GCM-16",
        "provider": "AES-GCM-16",
    }
    assert descriptor["params"] == {}
