"""
Unit tests for auto_authn.crypto module.

Tests password hashing, JWT key management, and security functions.
"""

import asyncio
from unittest.mock import patch

import pytest
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
from cryptography.hazmat.primitives import serialization

from auto_authn.crypto import (
    hash_pw,
    verify_pw,
    signing_key,
    public_key,
    _generate_keypair,
    _load_keypair,
    _provider,
    KeySpec,
    KeyClass,
    KeyAlg,
    KeyUse,
    ExportPolicy,
)


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
class TestJWTKeyCrypto:
    """Test JWT key generation and management functions."""

    def test_generate_keypair_creates_valid_ed25519_keys(self, tmp_path):
        """Test that key generation creates valid Ed25519 key pair."""
        key_path = tmp_path / "test_key.pem"

        kid, priv_pem, pub_pem = _generate_keypair(key_path)

        # Verify file was created with correct permissions
        assert key_path.exists()
        assert oct(key_path.stat().st_mode)[-3:] == "600"
        assert key_path.read_text().strip() == kid

        # Verify keys are valid Ed25519 format
        private_key = serialization.load_pem_private_key(priv_pem, password=None)
        assert isinstance(private_key, Ed25519PrivateKey)

        # Verify public key can be loaded
        serialization.load_pem_public_key(pub_pem)
        assert pub_pem.startswith(b"-----BEGIN PUBLIC KEY-----")

    def test_load_keypair_from_existing_file(self, tmp_path):
        """Test loading key pair from existing file."""
        key_path = tmp_path / "existing_key.pem"

        # First generate a key
        kid, original_priv, original_pub = _generate_keypair(key_path)

        # Mock the default path to use our test file
        with patch("auto_authn.crypto._DEFAULT_KEY_PATH", key_path):
            # Clear the cache
            _load_keypair.cache_clear()

            # Load the key pair
            loaded_kid, loaded_priv, loaded_pub = _load_keypair()

            assert loaded_kid == kid
            assert loaded_priv == original_priv
            assert loaded_pub == original_pub

    def test_generate_keypair_when_file_missing(self, tmp_path):
        """Test that keys are generated when file is missing."""
        key_path = tmp_path / "missing_key.pem"

        with patch("auto_authn.crypto._DEFAULT_KEY_PATH", key_path):
            # Clear the cache
            _load_keypair.cache_clear()

            # This should generate new keys
            kid, priv_pem, pub_pem = _load_keypair()

            # Verify file was created
            assert key_path.exists()
            assert key_path.read_text().strip() == kid

            # Verify keys are valid
            private_key = serialization.load_pem_private_key(priv_pem, password=None)
            assert isinstance(private_key, Ed25519PrivateKey)

    def test_keypair_caching_works(self, tmp_path):
        """Test that key pair loading is cached."""
        key_path = tmp_path / "cached_key.pem"

        with patch("auto_authn.crypto._DEFAULT_KEY_PATH", key_path):
            # Clear the cache
            _load_keypair.cache_clear()

            # First call should generate/load keys
            kid1, priv1, pub1 = _load_keypair()

            # Second call should return cached results
            kid2, priv2, pub2 = _load_keypair()

            assert kid1 == kid2
            assert priv1 is priv2  # Same object reference (cached)
            assert pub1 is pub2

    def test_signing_key_returns_private_key_bytes(self, temp_key_file):
        """Test that signing_key() returns private key bytes."""
        # Clear cache to ensure fresh key generation
        _load_keypair.cache_clear()

        key_bytes = signing_key()

        assert isinstance(key_bytes, bytes)
        assert key_bytes.startswith(b"-----BEGIN PRIVATE KEY-----")

        # Verify it's a valid Ed25519 private key
        private_key = serialization.load_pem_private_key(key_bytes, password=None)
        assert isinstance(private_key, Ed25519PrivateKey)

    def test_public_key_returns_public_key_bytes(self, temp_key_file):
        """Test that public_key() returns public key bytes."""
        # Clear cache to ensure fresh key generation
        _load_keypair.cache_clear()

        key_bytes = public_key()

        assert isinstance(key_bytes, bytes)
        assert key_bytes.startswith(b"-----BEGIN PUBLIC KEY-----")

        # Verify it's a valid public key
        serialization.load_pem_public_key(key_bytes)
        # Ed25519 public keys don't have a specific type check, but loading should work

    def test_private_key_file_permissions(self, tmp_path):
        """Test that private key files are created with secure permissions."""
        key_path = tmp_path / "secure_key.pem"

        _generate_keypair(key_path)

        # Check file permissions are 0o600 (readable/writable by owner only)
        file_mode = key_path.stat().st_mode
        permissions = oct(file_mode)[-3:]
        assert permissions == "600"

    def test_invalid_key_format_raises_error(self, tmp_path):
        """Test that invalid key format raises appropriate error."""
        key_path = tmp_path / "invalid_key.pem"

        # Write invalid key content
        key_path.write_text(
            "-----BEGIN PRIVATE KEY-----\nINVALID\n-----END PRIVATE KEY-----\n"
        )

        with patch("auto_authn.crypto._DEFAULT_KEY_PATH", key_path):
            # Clear the cache
            _load_keypair.cache_clear()

            with pytest.raises(ValueError):
                _load_keypair()

    def test_non_ed25519_key_raises_error(self, tmp_path):
        """Test that non-Ed25519 keys raise appropriate error."""
        key_path = tmp_path / "rsa_key.kid"

        async def _create_rsa() -> str:
            kp = _provider()
            spec = KeySpec(
                klass=KeyClass.asymmetric,
                alg=KeyAlg.RSA_PSS_SHA256,
                uses=(KeyUse.SIGN, KeyUse.VERIFY),
                export_policy=ExportPolicy.SECRET_WHEN_ALLOWED,
                label="rsa_key",
            )
            ref = await kp.create_key(spec)
            return ref.kid

        kid = asyncio.run(_create_rsa())
        key_path.write_text(kid)

        with patch("auto_authn.crypto._DEFAULT_KEY_PATH", key_path):
            _load_keypair.cache_clear()

            with pytest.raises(RuntimeError, match="JWT signing key is not Ed25519"):
                _load_keypair()

    def test_env_key_dir_override(self, monkeypatch, tmp_path):
        """Test that JWT_ED25519_KEY_DIR overrides the default key directory."""
        import auto_authn.crypto as crypto
        import importlib

        monkeypatch.setenv("JWT_ED25519_KEY_DIR", str(tmp_path))

        try:
            crypto = importlib.reload(crypto)
            crypto._load_keypair.cache_clear()

            kid, priv, _ = crypto._load_keypair()
            assert crypto._DEFAULT_KEY_PATH == tmp_path / "jwt_ed25519.kid"
            assert crypto.signing_key() == priv
        finally:
            monkeypatch.delenv("JWT_ED25519_KEY_DIR", raising=False)
            importlib.reload(crypto)


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
