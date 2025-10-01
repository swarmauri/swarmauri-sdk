import pytest

from swarmauri_cipher_suite_xades import XadesCipherSuite


@pytest.fixture
def cipher_suite() -> XadesCipherSuite:
    return XadesCipherSuite()


# Standard component tests
@pytest.mark.unit
def test_ubc_resource(cipher_suite: XadesCipherSuite) -> None:
    assert cipher_suite.resource == "CipherSuite"


@pytest.mark.unit
def test_ubc_type(cipher_suite: XadesCipherSuite) -> None:
    assert cipher_suite.type == "XadesCipherSuite"


@pytest.mark.unit
def test_initialization(cipher_suite: XadesCipherSuite) -> None:
    assert isinstance(cipher_suite.id, str)


@pytest.mark.unit
def test_serialization(cipher_suite: XadesCipherSuite) -> None:
    restored = XadesCipherSuite.model_validate_json(cipher_suite.model_dump_json())
    assert restored.id == cipher_suite.id


@pytest.mark.unit
def test_suite_identifier(cipher_suite: XadesCipherSuite) -> None:
    assert cipher_suite.suite_id() == "xades"


# Cipher-suite specific behavior
@pytest.mark.unit
def test_supports_expected_algorithms(cipher_suite: XadesCipherSuite) -> None:
    supports = cipher_suite.supports()
    assert set(supports.keys()) == {"sign", "verify"}
    assert set(supports["sign"]) == {"RSA-PSS-SHA256", "ECDSA-SHA256", "EdDSA"}
    assert supports["sign"] == supports["verify"]


@pytest.mark.unit
@pytest.mark.parametrize("operation", ["sign", "verify"])
def test_default_alg(cipher_suite: XadesCipherSuite, operation: str) -> None:
    assert cipher_suite.default_alg(operation) == "RSA-PSS-SHA256"


@pytest.mark.unit
def test_features_descriptor(cipher_suite: XadesCipherSuite) -> None:
    features = cipher_suite.features()
    assert features["suite"] == "xades"
    assert features["version"] == 1
    assert features["ops"]["sign"]["default"] == "RSA-PSS-SHA256"
    assert set(features["dialects"]["xmlsig"]) == {
        "RSA-PSS-SHA256",
        "ECDSA-SHA256",
        "EdDSA",
    }
    assert features["constraints"]["canonicalization"] == [
        "http://www.w3.org/TR/2001/REC-xml-c14n-20010315",
        "http://www.w3.org/2001/10/xml-exc-c14n#",
    ]


@pytest.mark.unit
def test_normalize_with_explicit_alg(cipher_suite: XadesCipherSuite) -> None:
    params = {
        "detached": True,
        "canonicalization": "http://www.w3.org/2001/10/xml-exc-c14n#",
    }
    descriptor = cipher_suite.normalize(
        op="sign",
        alg="ECDSA-SHA256",
        params=params,
    )

    assert descriptor["op"] == "sign"
    assert descriptor["alg"] == "ECDSA-SHA256"
    assert descriptor["dialect"] == "xmlsig"
    assert descriptor["mapped"] == {
        "xmlsig": "ECDSA-SHA256",
        "provider": "ECDSA-SHA256",
    }
    assert descriptor["params"] == params
    assert descriptor["constraints"] == {}
    assert descriptor["policy"] == {}


@pytest.mark.unit
def test_normalize_defaults(cipher_suite: XadesCipherSuite) -> None:
    descriptor = cipher_suite.normalize(op="verify")

    assert descriptor["alg"] == "RSA-PSS-SHA256"
    assert descriptor["dialect"] == "xmlsig"
    assert descriptor["mapped"] == {
        "xmlsig": "RSA-PSS-SHA256",
        "provider": "RSA-PSS-SHA256",
    }
    assert descriptor["params"] == {}
    assert descriptor["policy"] == {}


@pytest.mark.unit
def test_normalize_rejects_unsupported_alg(cipher_suite: XadesCipherSuite) -> None:
    with pytest.raises(ValueError):
        cipher_suite.normalize(op="sign", alg="RSA-PSS-SHA512")
