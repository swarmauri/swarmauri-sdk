import pytest

from swarmauri_cipher_suite_mlkem import MlkemCipherSuite


@pytest.fixture
def cipher_suite() -> MlkemCipherSuite:
    return MlkemCipherSuite()


# Standard component tests
@pytest.mark.unit
def test_ubc_resource(cipher_suite: MlkemCipherSuite) -> None:
    assert cipher_suite.resource == "CipherSuite"


@pytest.mark.unit
def test_ubc_type(cipher_suite: MlkemCipherSuite) -> None:
    assert cipher_suite.type == "MlkemCipherSuite"


@pytest.mark.unit
def test_initialization(cipher_suite: MlkemCipherSuite) -> None:
    assert isinstance(cipher_suite.id, str)


@pytest.mark.unit
def test_serialization(cipher_suite: MlkemCipherSuite) -> None:
    restored = MlkemCipherSuite.model_validate_json(cipher_suite.model_dump_json())
    assert restored.id == cipher_suite.id


@pytest.mark.unit
def test_suite_identifier(cipher_suite: MlkemCipherSuite) -> None:
    assert cipher_suite.suite_id() == "mlkem"


# Cipher-suite specific behavior
@pytest.mark.unit
def test_supports_expected_algorithms(cipher_suite: MlkemCipherSuite) -> None:
    supports = cipher_suite.supports()

    assert set(supports.keys()) == {"wrap", "unwrap", "seal", "unseal"}
    for algorithms in supports.values():
        assert tuple(algorithms) == ("mlkem512", "mlkem768", "mlkem1024")


@pytest.mark.unit
@pytest.mark.parametrize("operation", ["wrap", "unwrap", "seal", "unseal"])
def test_default_alg(cipher_suite: MlkemCipherSuite, operation: str) -> None:
    assert cipher_suite.default_alg(operation) == "mlkem768"


@pytest.mark.unit
def test_features_descriptor(cipher_suite: MlkemCipherSuite) -> None:
    features = cipher_suite.features()

    assert features["suite"] == "mlkem"
    assert features["dialects"]["tls"] == ["MLKEM512", "MLKEM768", "MLKEM1024"]
    assert features["ops"]["wrap"]["default"] == "mlkem768"
    assert (
        features["constraints"]["kem"]["variants"]["mlkem512"]["ciphertextLen"] == 768
    )


@pytest.mark.unit
def test_normalize_with_alias(cipher_suite: MlkemCipherSuite) -> None:
    descriptor = cipher_suite.normalize(op="seal", alg="ML-KEM-512")

    assert descriptor["alg"] == "mlkem512"
    assert descriptor["mapped"]["jwa"] == "ML-KEM-512"
    assert descriptor["params"]["secretKeyLen"] == 1632


@pytest.mark.unit
def test_normalize_defaults_when_alg_missing(cipher_suite: MlkemCipherSuite) -> None:
    descriptor = cipher_suite.normalize(op="wrap")

    assert descriptor["alg"] == "mlkem768"
    assert descriptor["params"]["ciphertextLen"] == 1088


@pytest.mark.unit
def test_normalize_allows_dialect_override(cipher_suite: MlkemCipherSuite) -> None:
    descriptor = cipher_suite.normalize(op="unwrap", dialect="provider")

    assert descriptor["dialect"] == "provider"
    assert descriptor["mapped"]["provider"].startswith("MLKEM")


@pytest.mark.unit
def test_normalize_rejects_invalid_alg(cipher_suite: MlkemCipherSuite) -> None:
    with pytest.raises(ValueError):
        cipher_suite.normalize(op="seal", alg="unknown")


@pytest.mark.unit
def test_normalize_rejects_invalid_dialect(cipher_suite: MlkemCipherSuite) -> None:
    with pytest.raises(ValueError):
        cipher_suite.normalize(op="seal", dialect="cms")
