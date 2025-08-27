"""Unit tests for ``auto_authn.jwtoken`` module."""

import base64
import json
import time
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import pytest
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

from auto_authn.jwtoken import (
    JWTCoder,
    InvalidTokenError,
    _ACCESS_TTL,
    _ALG,
    _REFRESH_TTL,
)


@pytest.mark.unit
class TestJWTCoder:
    """Test JWTCoder class for JWT token operations."""

    def setup_method(self):
        """Set up test fixtures for each test method."""
        # Generate a valid Ed25519 key pair for testing
        private_key_obj = Ed25519PrivateKey.generate()
        public_key_obj = private_key_obj.public_key()

        self.test_private_key = private_key_obj.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )

        self.test_public_key = public_key_obj.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

    def create_jwt_coder(self):
        """Create a JWTCoder instance with test keys."""
        return JWTCoder(self.test_private_key, self.test_public_key)

    def test_jwt_coder_initialization(self):
        """JWTCoder can sign and decode using provided keys."""
        coder = JWTCoder(self.test_private_key, self.test_public_key)

        token = coder.sign(sub="a", tid="t")
        payload = coder.decode(token)

        assert payload["sub"] == "a"
        assert payload["tid"] == "t"

    def test_default_factory_method(self):
        """JWTCoder.default() returns a working instance."""
        coder = JWTCoder.default()

        token = coder.sign(sub="a", tid="t")
        payload = coder.decode(token)

        assert payload["sub"] == "a"
        assert payload["tid"] == "t"

    def test_sign_token_with_required_claims(self):
        """Test signing a token with required claims."""
        coder = self.create_jwt_coder()

        sub = str(uuid4())
        tid = str(uuid4())

        token = coder.sign(sub=sub, tid=tid)

        # Verify it's a valid token string
        assert isinstance(token, str)
        assert len(token) > 50  # JWT tokens are typically much longer

        # Decode and verify payload
        payload = coder.decode(token)
        assert payload["sub"] == sub
        assert payload["tid"] == tid
        assert payload["typ"] == "access"  # Default type
        assert "iat" in payload
        assert "exp" in payload

    def test_sign_token_with_custom_claims(self):
        """Test signing a token with custom claims."""
        coder = self.create_jwt_coder()

        sub = str(uuid4())
        tid = str(uuid4())
        custom_claims = {
            "scopes": ["read", "write"],
            "role": "admin",
            "custom_field": "test_value",
        }

        token = coder.sign(sub=sub, tid=tid, **custom_claims)
        payload = coder.decode(token)

        # Verify required claims
        assert payload["sub"] == sub
        assert payload["tid"] == tid

        # Verify custom claims
        assert payload["scopes"] == ["read", "write"]
        assert payload["role"] == "admin"
        assert payload["custom_field"] == "test_value"

    def test_sign_token_with_custom_ttl(self):
        """Test signing a token with custom TTL."""
        coder = self.create_jwt_coder()

        sub = str(uuid4())
        tid = str(uuid4())
        custom_ttl = timedelta(minutes=30)

        before_signing = datetime.now(timezone.utc) - timedelta(
            seconds=1
        )  # More lenient
        token = coder.sign(sub=sub, tid=tid, ttl=custom_ttl)
        after_signing = datetime.now(timezone.utc) + timedelta(
            seconds=1
        )  # More lenient

        payload = coder.decode(token)
        exp_time = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
        iat_time = datetime.fromtimestamp(payload["iat"], tz=timezone.utc)

        # Verify the token expires in approximately 30 minutes
        actual_ttl = exp_time - iat_time
        assert abs(actual_ttl - custom_ttl) < timedelta(seconds=5)

        # Verify issued time is reasonable (more lenient timing)
        assert before_signing <= iat_time <= after_signing

    def test_sign_token_with_custom_type(self):
        """Test signing a token with custom type."""
        coder = self.create_jwt_coder()

        sub = str(uuid4())
        tid = str(uuid4())

        token = coder.sign(sub=sub, tid=tid, typ="refresh")
        payload = coder.decode(token)

        assert payload["typ"] == "refresh"

    def test_sign_pair_returns_access_and_refresh(self):
        """Test sign_pair returns both access and refresh tokens."""
        coder = self.create_jwt_coder()

        sub = str(uuid4())
        tid = str(uuid4())

        access_token, refresh_token = coder.sign_pair(sub=sub, tid=tid)

        # Verify both are valid tokens
        assert isinstance(access_token, str)
        assert isinstance(refresh_token, str)
        assert access_token != refresh_token

        # Decode and verify access token
        access_payload = coder.decode(access_token)
        assert access_payload["sub"] == sub
        assert access_payload["tid"] == tid
        assert access_payload["typ"] == "access"

        # Decode and verify refresh token
        refresh_payload = coder.decode(refresh_token)
        assert refresh_payload["sub"] == sub
        assert refresh_payload["tid"] == tid
        assert refresh_payload["typ"] == "refresh"

    def test_sign_pair_with_extra_claims(self):
        """Test sign_pair with additional claims."""
        coder = self.create_jwt_coder()

        sub = str(uuid4())
        tid = str(uuid4())
        extra_claims = {"role": "admin", "scopes": ["read", "write"]}

        access_token, refresh_token = coder.sign_pair(sub=sub, tid=tid, **extra_claims)

        # Verify extra claims are in both tokens
        access_payload = coder.decode(access_token)
        refresh_payload = coder.decode(refresh_token)

        for claim, value in extra_claims.items():
            assert access_payload[claim] == value
            assert refresh_payload[claim] == value

    def test_decode_valid_token(self):
        """Test decoding a valid token."""
        coder = self.create_jwt_coder()

        sub = str(uuid4())
        tid = str(uuid4())
        token = coder.sign(sub=sub, tid=tid)

        payload = coder.decode(token)

        assert payload["sub"] == sub
        assert payload["tid"] == tid
        assert "iat" in payload
        assert "exp" in payload

    def test_decode_expired_token(self):
        """Test decoding an expired token raises error."""
        coder = self.create_jwt_coder()

        sub = str(uuid4())
        tid = str(uuid4())
        # Create token with very short TTL
        token = coder.sign(sub=sub, tid=tid, ttl=timedelta(seconds=-1))

        # Should raise InvalidTokenError when trying to decode expired token
        with pytest.raises(InvalidTokenError):
            coder.decode(token)

    def test_decode_expired_token_with_verification_disabled(self):
        """Test decoding expired token with expiration verification disabled."""
        coder = self.create_jwt_coder()

        sub = str(uuid4())
        tid = str(uuid4())
        # Create token with very short TTL
        token = coder.sign(sub=sub, tid=tid, ttl=timedelta(seconds=-1))

        # Should succeed when expiration verification is disabled
        payload = coder.decode(token, verify_exp=False)
        assert payload["sub"] == sub
        assert payload["tid"] == tid

    def test_decode_invalid_signature(self):
        """Test decoding a token with invalid signature."""
        coder = self.create_jwt_coder()

        # Create a different coder with different keys
        different_private_key_obj = Ed25519PrivateKey.generate()
        different_public_key_obj = different_private_key_obj.public_key()

        different_private_key = different_private_key_obj.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )

        different_public_key = different_public_key_obj.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

        different_coder = JWTCoder(different_private_key, different_public_key)

        sub = str(uuid4())
        tid = str(uuid4())
        token = different_coder.sign(sub=sub, tid=tid)

        # Should raise InvalidTokenError when verifying with wrong key
        with pytest.raises(InvalidTokenError):
            coder.decode(token)

    def test_decode_malformed_token(self):
        """Test decoding a malformed token."""
        coder = self.create_jwt_coder()

        malformed_tokens = [
            "not.a.jwt",
            "invalid-token",
            "",
            "a.b",  # Too few parts
            "a.b.c.d",  # Too many parts
        ]

        for malformed_token in malformed_tokens:
            with pytest.raises(InvalidTokenError):
                coder.decode(malformed_token)

    def test_refresh_token_flow(self):
        """Test complete refresh token flow."""
        coder = self.create_jwt_coder()

        sub = str(uuid4())
        tid = str(uuid4())
        extra_claims = {"role": "user", "scopes": ["read"]}

        # Create initial token pair
        original_access, original_refresh = coder.sign_pair(
            sub=sub, tid=tid, **extra_claims
        )

        # Add a longer delay to ensure different timestamps
        time.sleep(1.1)  # Ensure at least 1 second difference

        # Use refresh token to get new token pair
        new_access, new_refresh = coder.refresh(original_refresh)

        # Verify new tokens are different from original
        assert new_access != original_access
        assert new_refresh != original_refresh

        # Verify new tokens have same claims (except iat/exp)
        new_access_payload = coder.decode(new_access)
        new_refresh_payload = coder.decode(new_refresh)

        assert new_access_payload["sub"] == sub
        assert new_access_payload["tid"] == tid
        assert new_access_payload["role"] == "user"
        assert new_access_payload["scopes"] == ["read"]

        assert new_refresh_payload["sub"] == sub
        assert new_refresh_payload["tid"] == tid
        assert new_refresh_payload["role"] == "user"
        assert new_refresh_payload["scopes"] == ["read"]

    def test_refresh_with_invalid_token(self):
        """Test refresh with invalid token raises error."""
        coder = self.create_jwt_coder()

        invalid_tokens = [
            "invalid-token",
            "not.a.jwt.token",
            "",
        ]

        for invalid_token in invalid_tokens:
            with pytest.raises(InvalidTokenError):
                coder.refresh(invalid_token)

    def test_refresh_with_access_token(self):
        """Test refresh with access token (should fail)."""
        coder = self.create_jwt_coder()

        sub = str(uuid4())
        tid = str(uuid4())

        # Create access token (not refresh token)
        access_token = coder.sign(sub=sub, tid=tid, typ="access")

        # Should raise error when trying to refresh with access token
        with pytest.raises(ValueError, match="token is not a refresh token"):
            coder.refresh(access_token)

    def test_refresh_with_expired_token(self):
        """Test refresh with expired refresh token."""
        coder = self.create_jwt_coder()

        sub = str(uuid4())
        tid = str(uuid4())

        # Create expired refresh token
        expired_refresh = coder.sign(
            sub=sub, tid=tid, typ="refresh", ttl=timedelta(seconds=-1)
        )

        # Should raise error when trying to refresh with expired token
        with pytest.raises(InvalidTokenError):
            coder.refresh(expired_refresh)

    def test_token_expiration_times(self):
        """Test that token expiration times match expected TTLs."""
        coder = self.create_jwt_coder()

        sub = str(uuid4())
        tid = str(uuid4())

        before_signing = datetime.now(timezone.utc) - timedelta(
            seconds=1
        )  # More lenient
        access_token, refresh_token = coder.sign_pair(sub=sub, tid=tid)
        after_signing = datetime.now(timezone.utc) + timedelta(
            seconds=1
        )  # More lenient

        access_payload = coder.decode(access_token)
        refresh_payload = coder.decode(refresh_token)

        access_exp = datetime.fromtimestamp(access_payload["exp"], tz=timezone.utc)
        refresh_exp = datetime.fromtimestamp(refresh_payload["exp"], tz=timezone.utc)

        access_iat = datetime.fromtimestamp(access_payload["iat"], tz=timezone.utc)
        refresh_iat = datetime.fromtimestamp(refresh_payload["iat"], tz=timezone.utc)

        # Verify access token TTL (should be ~60 minutes)
        access_ttl = access_exp - access_iat
        assert abs(access_ttl - _ACCESS_TTL) < timedelta(seconds=5)

        # Verify refresh token TTL (should be ~7 days)
        refresh_ttl = refresh_exp - refresh_iat
        assert abs(refresh_ttl - _REFRESH_TTL) < timedelta(seconds=5)

        # Verify issued times are reasonable (more lenient timing)
        assert before_signing <= access_iat <= after_signing
        assert before_signing <= refresh_iat <= after_signing

    def test_algorithm_consistency(self):
        """Test that tokens use the expected algorithm."""
        coder = self.create_jwt_coder()

        sub = str(uuid4())
        tid = str(uuid4())
        token = coder.sign(sub=sub, tid=tid)

        # Decode header to check algorithm without PyJWT.  The JWT segment may
        # omit padding so we add it back before decoding to avoid "incorrect
        # padding" errors on tokens whose header length is not divisible by 4.
        header_b64 = token.split(".")[0]
        padding = "=" * (-len(header_b64) % 4)
        header = json.loads(base64.urlsafe_b64decode(header_b64 + padding).decode())
        assert header["alg"] == _ALG  # Should be "EdDSA"

    def test_multiple_coders_independence(self):
        """Test that multiple JWTCoder instances work independently."""
        # Create two different coders with different keys
        coder1 = self.create_jwt_coder()

        # Generate different keys for second coder
        different_private_key_obj = Ed25519PrivateKey.generate()
        different_public_key_obj = different_private_key_obj.public_key()

        different_private_key = different_private_key_obj.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        )

        different_public_key = different_public_key_obj.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )

        coder2 = JWTCoder(different_private_key, different_public_key)

        sub = str(uuid4())
        tid = str(uuid4())

        # Create tokens with each coder
        token1 = coder1.sign(sub=sub, tid=tid)
        token2 = coder2.sign(sub=sub, tid=tid)

        # Each coder should only be able to decode its own tokens
        payload1 = coder1.decode(token1)
        payload2 = coder2.decode(token2)

        assert payload1["sub"] == sub
        assert payload2["sub"] == sub

        # Cross-verification should fail
        with pytest.raises(InvalidTokenError):
            coder1.decode(token2)

        with pytest.raises(InvalidTokenError):
            coder2.decode(token1)


@pytest.mark.unit
class TestJWTCoderWithRealKeys:
    """Test JWTCoder with real key generation from crypto module."""

    def test_default_coder_with_temp_keys(self, temp_key_file):
        """Test JWTCoder.default() with temporary key file."""
        # This will use the temp_key_file fixture which creates a key
        coder = JWTCoder.default()

        sub = str(uuid4())
        tid = str(uuid4())

        # Should be able to sign and decode tokens
        token = coder.sign(sub=sub, tid=tid)
        payload = coder.decode(token)

        assert payload["sub"] == sub
        assert payload["tid"] == tid

    def test_sign_pair_with_real_keys(self, temp_key_file):
        """Test token pair generation with real keys."""
        coder = JWTCoder.default()

        sub = str(uuid4())
        tid = str(uuid4())

        access_token, refresh_token = coder.sign_pair(sub=sub, tid=tid)

        # Both tokens should be decodable
        access_payload = coder.decode(access_token)
        refresh_payload = coder.decode(refresh_token)

        assert access_payload["sub"] == sub
        assert refresh_payload["sub"] == sub
        assert access_payload["typ"] == "access"
        assert refresh_payload["typ"] == "refresh"

    def test_refresh_flow_with_real_keys(self, temp_key_file):
        """Test complete refresh flow with real keys."""
        coder = JWTCoder.default()

        sub = str(uuid4())
        tid = str(uuid4())

        # Create initial tokens
        original_access, original_refresh = coder.sign_pair(sub=sub, tid=tid)

        # Add a longer delay to ensure different timestamps
        time.sleep(1.1)  # Ensure at least 1 second difference

        # Refresh to get new tokens
        new_access, new_refresh = coder.refresh(original_refresh)

        # All tokens should be valid and different
        assert new_access != original_access
        assert new_refresh != original_refresh

        new_access_payload = coder.decode(new_access)
        new_refresh_payload = coder.decode(new_refresh)

        assert new_access_payload["sub"] == sub
        assert new_refresh_payload["sub"] == sub


@pytest.mark.unit
class TestJWTConstants:
    """Test JWT module constants and configuration."""

    def test_algorithm_constant(self):
        """Test that the algorithm constant is correct."""
        assert _ALG == "EdDSA"

    def test_ttl_constants(self):
        """Test that TTL constants have expected values."""
        assert _ACCESS_TTL == timedelta(minutes=60)
        assert _REFRESH_TTL == timedelta(days=7)

        # Verify they're reasonable values
        assert _ACCESS_TTL.total_seconds() == 3600  # 1 hour
        assert _REFRESH_TTL.total_seconds() == 604800  # 7 days

    def test_access_token_shorter_than_refresh(self):
        """Test that access token TTL is shorter than refresh token TTL."""
        assert _ACCESS_TTL < _REFRESH_TTL
