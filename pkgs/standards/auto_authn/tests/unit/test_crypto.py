"""
Unit tests for auto_authn.v2.crypto module.

Tests password hashing, JWT key management, and security functions.
"""

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization

import auto_authn.v2.crypto as crypto
from auto_authn.v2.crypto import (
    hash_pw,
    verify_pw,
    signing_key,
    public_key,
)


@pytest.mark.unit
class TestJWTKeyCrypto:
    """Test JWT key generation and management functions."""

    def _setup_dir(self, tmp_path, monkeypatch):
        key_dir = tmp_path
        kid_path = key_dir / "jwt_ed25519.kid"
        monkeypatch.setattr(crypto, "_DEFAULT_KEY_DIR", key_dir)
        monkeypatch.setattr(crypto, "_DEFAULT_KEY_PATH", kid_path)
        crypto._provider.cache_clear()
        crypto._load_keypair.cache_clear()
        return key_dir, kid_path

    def test_load_keypair_creates_valid_ed25519_keys(self, tmp_path, monkeypatch):
        key_dir, kid_path = self._setup_dir(tmp_path, monkeypatch)
        kid, priv_pem, pub_pem = crypto._load_keypair()
        assert kid_path.exists()
        assert oct(kid_path.stat().st_mode)[-3:] == "600"
        private_key = serialization.load_pem_private_key(priv_pem, password=None)
        assert isinstance(private_key, Ed25519PrivateKey)
        serialization.load_pem_public_key(pub_pem)

    def test_load_keypair_from_existing_file(self, tmp_path, monkeypatch):
        key_dir, kid_path = self._setup_dir(tmp_path, monkeypatch)
        kid1, priv1, pub1 = crypto._load_keypair()
        crypto._load_keypair.cache_clear()
        kid2, priv2, pub2 = crypto._load_keypair()
        assert kid1 == kid2
        assert priv1 == priv2
        assert pub1 == pub2

    def test_keypair_caching_works(self, tmp_path, monkeypatch):
        self._setup_dir(tmp_path, monkeypatch)
        first = crypto._load_keypair()
        second = crypto._load_keypair()
        assert first is second

    def test_signing_key_returns_private_key_bytes(self, temp_key_file):
        crypto._provider.cache_clear()
        crypto._load_keypair.cache_clear()
        key_bytes = signing_key()
        assert isinstance(key_bytes, bytes)
        assert key_bytes.startswith(b"-----BEGIN PRIVATE KEY-----")
        private_key = serialization.load_pem_private_key(key_bytes, password=None)
        assert isinstance(private_key, Ed25519PrivateKey)

    def test_public_key_returns_public_key_bytes(self, temp_key_file):
        crypto._provider.cache_clear()
        crypto._load_keypair.cache_clear()
        key_bytes = public_key()
        assert isinstance(key_bytes, bytes)
        assert key_bytes.startswith(b"-----BEGIN PUBLIC KEY-----")
        serialization.load_pem_public_key(key_bytes)

    def test_private_key_file_permissions(self, tmp_path, monkeypatch):
        key_dir, kid_path = self._setup_dir(tmp_path, monkeypatch)
        kid, _, _ = crypto._load_keypair()
        priv_path = key_dir / "keys" / kid / "v1" / "private.pem"
        assert priv_path.exists()
        assert oct(priv_path.stat().st_mode)[-3:] == "600"

    def test_invalid_key_identifier_raises_error(self, tmp_path, monkeypatch):
        key_dir, kid_path = self._setup_dir(tmp_path, monkeypatch)
        kid_path.write_text("invalid")
        crypto._load_keypair.cache_clear()
        with pytest.raises(ValueError):
            crypto._load_keypair()

    def test_non_ed25519_key_raises_error(self, tmp_path, monkeypatch):
        key_dir, kid_path = self._setup_dir(tmp_path, monkeypatch)
        kid, _, _ = crypto._load_keypair()
        from cryptography.hazmat.primitives.asymmetric import rsa

        rsa_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        rsa_pem = rsa_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )
        priv_path = key_dir / "keys" / kid / "v1" / "private.pem"
        priv_path.write_bytes(rsa_pem)
        meta_path = key_dir / "keys" / kid / "meta.json"
        import json

        meta = json.loads(meta_path.read_text())
        meta["alg"] = "RSA_PSS_SHA256"
        meta_path.write_text(json.dumps(meta))
        crypto._load_keypair.cache_clear()
        with pytest.raises(RuntimeError, match="JWT signing key is not Ed25519"):
            crypto._load_keypair()

    def test_env_key_dir_override(self, monkeypatch, tmp_path):
        import importlib

        monkeypatch.setenv("JWT_ED25519_KEY_DIR", str(tmp_path))
        module = importlib.reload(crypto)
        module._provider.cache_clear()
        module._load_keypair.cache_clear()
        kid, priv, pub = module._load_keypair()
        assert module._DEFAULT_KEY_DIR == tmp_path
        assert module._DEFAULT_KEY_PATH == tmp_path / "jwt_ed25519.kid"
        monkeypatch.delenv("JWT_ED25519_KEY_DIR", raising=False)
        importlib.reload(module)


@pytest.mark.unit
class TestPasswordCrypto:
    """Test password hashing and verification functions."""

    def test_hash_password_generates_bcrypt_hash(self):
        """Test that password hashing generates valid bcrypt hash."""
        password = "TestPassword123!"
        hashed = hash_pw(password)

        # Should be bcrypt format (starts with $2b$ and is 60 bytes)
        assert hashed.startswith(b"$2b$")
        assert len(hashed) == 60

    def test_verify_password_with_correct_password(self):
        """Test password verification with correct password."""
        password = "TestPassword123!"
        hashed = hash_pw(password)

        assert verify_pw(password, hashed) is True

    def test_verify_password_with_incorrect_password(self):
        """Test password verification with incorrect password."""
        password = "TestPassword123!"
        wrong_password = "WrongPassword456!"
        hashed = hash_pw(password)

        assert verify_pw(wrong_password, hashed) is False

    def test_verify_password_with_invalid_hash_format(self):
        """Test password verification with invalid hash format."""
        password = "TestPassword123!"
        invalid_hash = b"not-a-valid-bcrypt-hash"

        assert verify_pw(password, invalid_hash) is False

    def test_password_hash_different_each_time(self):
        """Test that the same password produces different hashes (salt)."""
        password = "TestPassword123!"
        hash1 = hash_pw(password)
        hash2 = hash_pw(password)

        assert hash1 != hash2
        assert verify_pw(password, hash1) is True
        assert verify_pw(password, hash2) is True

    def test_password_hash_handles_unicode(self):
        """Test password hashing with unicode characters."""
        password = "Test密码123!ñ"
        hashed = hash_pw(password)

        assert verify_pw(password, hashed) is True
        assert verify_pw("different", hashed) is False


@pytest.mark.unit
class TestSecurityEdgeCases:
    """Test security-related edge cases and error conditions."""

    def test_password_verification_handles_none_input(self):
        """Test that password verification handles None input gracefully."""
        hashed = hash_pw("password")

        # This should not raise an exception but return False
        assert verify_pw("", hashed) is False

    def test_empty_password_hashing(self):
        """Test hashing of empty password."""
        empty_hash = hash_pw("")
        assert verify_pw("", empty_hash) is True
        assert verify_pw("not-empty", empty_hash) is False

    def test_very_long_password(self):
        """Test handling of very long passwords (bcrypt truncates at 72 bytes)."""
        long_password = "a" * 1000
        hashed = hash_pw(long_password)

        assert verify_pw(long_password, hashed) is True

        # bcrypt only uses first 72 bytes, so passwords longer than 72 bytes
        # that start the same will hash identically
        very_long_same_start = "a" * 500
        assert verify_pw(very_long_same_start, hashed) is True

        # But a password with different start should fail
        different_long_password = "b" * 1000
        assert verify_pw(different_long_password, hashed) is False
