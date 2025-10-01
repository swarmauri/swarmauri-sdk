import pytest

from swarmauri_cipher_suite_ssh import SshCipherSuite


@pytest.fixture
def cipher_suite() -> SshCipherSuite:
    return SshCipherSuite()


# Standard component tests
@pytest.mark.unit
def test_ubc_resource(cipher_suite: SshCipherSuite) -> None:
    assert cipher_suite.resource == "CipherSuite"


@pytest.mark.unit
def test_ubc_type(cipher_suite: SshCipherSuite) -> None:
    assert cipher_suite.type == "SshCipherSuite"


@pytest.mark.unit
def test_initialization(cipher_suite: SshCipherSuite) -> None:
    assert isinstance(cipher_suite.id, str)


@pytest.mark.unit
def test_serialization(cipher_suite: SshCipherSuite) -> None:
    restored = SshCipherSuite.model_validate_json(cipher_suite.model_dump_json())
    assert restored.id == cipher_suite.id


@pytest.mark.unit
def test_suite_identifier(cipher_suite: SshCipherSuite) -> None:
    assert cipher_suite.suite_id() == "ssh"


# Cipher-suite specific behavior
@pytest.mark.unit
def test_supports_expected_algorithms(cipher_suite: SshCipherSuite) -> None:
    supports = cipher_suite.supports()
    assert set(supports.keys()) == {"encrypt", "decrypt"}
    expected = {
        "chacha20-poly1305@openssh.com",
        "aes256-gcm@openssh.com",
    }
    assert set(supports["encrypt"]) == expected
    assert supports["encrypt"] == supports["decrypt"]


@pytest.mark.unit
@pytest.mark.parametrize("operation", ["encrypt", "decrypt"])
def test_default_alg(cipher_suite: SshCipherSuite, operation: str) -> None:
    assert cipher_suite.default_alg(operation) == "chacha20-poly1305@openssh.com"


@pytest.mark.unit
def test_features_descriptor(cipher_suite: SshCipherSuite) -> None:
    features = cipher_suite.features()
    assert features["suite"] == "ssh"
    assert features["version"] == 1
    assert features["dialects"]["ssh"] == [
        "chacha20-poly1305@openssh.com",
        "aes256-gcm@openssh.com",
    ]
    assert features["constraints"] == {
        "kex": ("curve25519-sha256", "ecdh-sha2-nistp256"),
        "host_key": ("ssh-ed25519", "rsa-sha2-256"),
        "mac": ("hmac-sha2-256",),
    }
    assert features["ops"]["encrypt"]["default"] == "chacha20-poly1305@openssh.com"
    assert set(features["ops"]["encrypt"]["allowed"]) == {
        "chacha20-poly1305@openssh.com",
        "aes256-gcm@openssh.com",
    }


@pytest.mark.unit
def test_normalize_with_explicit_alg(cipher_suite: SshCipherSuite) -> None:
    descriptor = cipher_suite.normalize(
        op="encrypt",
        alg="aes256-gcm@openssh.com",
        params={"compress": False},
    )

    assert descriptor["op"] == "encrypt"
    assert descriptor["alg"] == "aes256-gcm@openssh.com"
    assert descriptor["dialect"] == "ssh"
    assert descriptor["mapped"] == {
        "ssh": "aes256-gcm@openssh.com",
        "provider": "aes256-gcm@openssh.com",
    }
    assert descriptor["params"] == {"compress": False}
    assert descriptor["constraints"] == {}
    assert descriptor["policy"] == cipher_suite.policy()


@pytest.mark.unit
def test_normalize_defaults(cipher_suite: SshCipherSuite) -> None:
    descriptor = cipher_suite.normalize(op="decrypt")

    assert descriptor["op"] == "decrypt"
    assert descriptor["alg"] == "chacha20-poly1305@openssh.com"
    assert descriptor["dialect"] == "ssh"
    assert descriptor["mapped"] == {
        "ssh": "chacha20-poly1305@openssh.com",
        "provider": "chacha20-poly1305@openssh.com",
    }
    assert descriptor["params"] == {}
    assert descriptor["constraints"] == {}
    assert descriptor["policy"] == cipher_suite.policy()


@pytest.mark.unit
def test_normalize_rejects_unsupported_alg(cipher_suite: SshCipherSuite) -> None:
    with pytest.raises(ValueError):
        cipher_suite.normalize(op="encrypt", alg="aes128-ctr")
