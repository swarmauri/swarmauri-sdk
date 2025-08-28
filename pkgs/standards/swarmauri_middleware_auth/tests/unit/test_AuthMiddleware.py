"""
Unit tests for AuthMiddleware with JWT authentication.
"""

import time
from unittest.mock import AsyncMock, Mock

import asyncio
import pytest
from fastapi import HTTPException, Request
from swarmauri_core.crypto.types import JWAAlg
from swarmauri_signing_jws import JwsSignerVerifier
from swarmauri_middleware_auth.AuthMiddleware import AuthMiddleware, InvalidTokenError


@pytest.fixture
def secret_key():
    """Fixture providing a test secret key."""
    return "test-secret-key-for-jwt-validation"


@pytest.fixture
def auth_middleware(secret_key):
    """Fixture providing an AuthMiddleware instance."""
    return AuthMiddleware(
        secret_key=secret_key,
        algorithm="HS256",
        verify_exp=True,
        verify_aud=False,
        audience=None,
        issuer=None,
    )


@pytest.fixture
def auth_middleware_with_audience(secret_key):
    """Fixture providing an AuthMiddleware instance with audience validation."""
    return AuthMiddleware(
        secret_key=secret_key,
        algorithm="HS256",
        verify_exp=True,
        verify_aud=True,
        audience="test-app",
        issuer="test-issuer",
    )


_signer = JwsSignerVerifier()


def _make_token(payload: dict, secret: str) -> str:
    return asyncio.run(
        _signer.sign_compact(
            payload=payload,
            alg=JWAAlg.HS256,
            key={"kind": "raw", "key": secret, "alg": "HS256"},
            typ="JWT",
        )
    )


@pytest.fixture
def valid_token(secret_key):
    """Fixture providing a valid JWT token."""
    payload = {
        "sub": "user123",
        "iat": int(time.time()),
        "exp": int(time.time()) + 3600,  # Expires in 1 hour
        "name": "Test User",
        "role": "user",
    }
    return _make_token(payload, secret_key)


@pytest.fixture
def expired_token(secret_key):
    """Fixture providing an expired JWT token."""
    payload = {
        "sub": "user123",
        "iat": int(time.time()) - 7200,  # Issued 2 hours ago
        "exp": int(time.time()) - 3600,  # Expired 1 hour ago
        "name": "Test User",
        "role": "user",
    }
    return _make_token(payload, secret_key)


@pytest.fixture
def invalid_signature_token(secret_key):
    """Fixture providing a token with invalid signature."""
    payload = {
        "sub": "user123",
        "iat": int(time.time()),
        "exp": int(time.time()) + 3600,
        "name": "Test User",
        "role": "user",
    }
    # Use a different secret key to create invalid signature
    return _make_token(payload, "wrong-secret-key")


@pytest.fixture
def token_with_audience(secret_key):
    """Fixture providing a token with audience claim."""
    payload = {
        "sub": "user123",
        "iat": int(time.time()),
        "exp": int(time.time()) + 3600,
        "aud": "test-app",
        "iss": "test-issuer",
        "name": "Test User",
        "role": "user",
    }
    return _make_token(payload, secret_key)


@pytest.fixture
def mock_request():
    """Fixture providing a mock request object."""
    request = Mock(spec=Request)
    request.headers = {}
    request.state = Mock()
    return request


@pytest.mark.unit
class TestAuthMiddleware:
    """Unit tests for AuthMiddleware class."""

    def test_init(self, secret_key):
        """Test AuthMiddleware initialization."""
        middleware = AuthMiddleware(
            secret_key=secret_key,
            algorithm="RS256",
            verify_exp=False,
            verify_aud=True,
            audience="my-app",
            issuer="my-service",
        )

        assert middleware.secret_key == secret_key
        assert middleware.algorithm == "RS256"
        assert middleware.verify_exp is False
        assert middleware.verify_aud is True
        assert middleware.audience == "my-app"
        assert middleware.issuer == "my-service"

    def test_ubc_type(self, auth_middleware):
        """Test that AuthMiddleware is registered as a MiddlewareBase type."""
        assert auth_middleware.type == "AuthMiddleware"

    def test_ubc_resource(self, auth_middleware):
        """Test that AuthMiddleware has a resource."""
        assert auth_middleware.resource == "Middleware"

    @pytest.mark.asyncio
    async def test_dispatch_missing_authorization_header(
        self, auth_middleware, mock_request
    ):
        """Test that missing Authorization header raises 401."""
        # Mock request without Authorization header
        mock_request.headers = {}

        call_next = AsyncMock()

        with pytest.raises(HTTPException) as exc_info:
            await auth_middleware.dispatch(mock_request, call_next)

        assert exc_info.value.status_code == 401
        assert "Missing Authorization header" in exc_info.value.detail
        call_next.assert_not_called()

    @pytest.mark.asyncio
    async def test_dispatch_invalid_header_format(self, auth_middleware, mock_request):
        """Test that invalid header format raises 401."""
        # Mock request with invalid header format
        mock_request.headers = {"Authorization": "InvalidFormat token123"}

        call_next = AsyncMock()

        with pytest.raises(HTTPException) as exc_info:
            await auth_middleware.dispatch(mock_request, call_next)

        assert exc_info.value.status_code == 401
        assert "Invalid token format" in exc_info.value.detail
        call_next.assert_not_called()

    @pytest.mark.asyncio
    async def test_dispatch_empty_token(self, auth_middleware, mock_request):
        """Test that empty token raises 401."""
        # Mock request with empty token
        mock_request.headers = {"Authorization": "Bearer "}

        call_next = AsyncMock()

        with pytest.raises(HTTPException) as exc_info:
            await auth_middleware.dispatch(mock_request, call_next)

        assert exc_info.value.status_code == 401
        assert "Invalid token format" in exc_info.value.detail
        call_next.assert_not_called()

    @pytest.mark.asyncio
    async def test_dispatch_valid_token(
        self, auth_middleware, mock_request, valid_token
    ):
        """Test successful authentication with valid token."""
        # Mock request with valid token
        mock_request.headers = {"Authorization": f"Bearer {valid_token}"}

        call_next = AsyncMock(return_value="success_response")

        response = await auth_middleware.dispatch(mock_request, call_next)

        assert response == "success_response"
        call_next.assert_called_once_with(mock_request)

        # Verify user data is added to request state
        assert hasattr(mock_request.state, "user")
        assert mock_request.state.user["sub"] == "user123"
        assert mock_request.state.user["name"] == "Test User"

    @pytest.mark.asyncio
    async def test_dispatch_expired_token(
        self, auth_middleware, mock_request, expired_token
    ):
        """Test that expired token raises 401."""
        # Mock request with expired token
        mock_request.headers = {"Authorization": f"Bearer {expired_token}"}

        call_next = AsyncMock()

        with pytest.raises(HTTPException) as exc_info:
            await auth_middleware.dispatch(mock_request, call_next)

        assert exc_info.value.status_code == 401
        assert "Token has expired" in exc_info.value.detail
        call_next.assert_not_called()

    @pytest.mark.asyncio
    async def test_dispatch_invalid_signature(
        self, auth_middleware, mock_request, invalid_signature_token
    ):
        """Test that token with invalid signature raises 401."""
        # Mock request with invalid signature token
        mock_request.headers = {"Authorization": f"Bearer {invalid_signature_token}"}

        call_next = AsyncMock()

        with pytest.raises(HTTPException) as exc_info:
            await auth_middleware.dispatch(mock_request, call_next)

        assert exc_info.value.status_code == 401
        assert "Invalid token signature" in exc_info.value.detail
        call_next.assert_not_called()

    @pytest.mark.asyncio
    async def test_dispatch_malformed_token(self, auth_middleware, mock_request):
        """Test that malformed token raises 401."""
        # Mock request with malformed token
        mock_request.headers = {"Authorization": "Bearer not.a.valid.jwt.token"}

        call_next = AsyncMock()

        with pytest.raises(HTTPException) as exc_info:
            await auth_middleware.dispatch(mock_request, call_next)

        assert exc_info.value.status_code == 401
        assert "Invalid token" in exc_info.value.detail
        call_next.assert_not_called()

    @pytest.mark.asyncio
    async def test_dispatch_with_audience_validation(
        self, auth_middleware_with_audience, mock_request, token_with_audience
    ):
        """Test successful authentication with audience validation."""
        # Mock request with token containing audience
        mock_request.headers = {"Authorization": f"Bearer {token_with_audience}"}

        call_next = AsyncMock(return_value="success_response")

        response = await auth_middleware_with_audience.dispatch(mock_request, call_next)

        assert response == "success_response"
        call_next.assert_called_once_with(mock_request)

        # Verify user data is added to request state
        assert hasattr(mock_request.state, "user")
        assert mock_request.state.user["sub"] == "user123"
        assert mock_request.state.user["aud"] == "test-app"
        assert mock_request.state.user["iss"] == "test-issuer"

    @pytest.mark.asyncio
    async def test_dispatch_invalid_audience(
        self, auth_middleware_with_audience, mock_request, valid_token
    ):
        """Test that token with wrong audience raises 401."""
        # Mock request with token that doesn't have the expected audience
        mock_request.headers = {"Authorization": f"Bearer {valid_token}"}

        call_next = AsyncMock()

        with pytest.raises(HTTPException) as exc_info:
            await auth_middleware_with_audience.dispatch(mock_request, call_next)

        assert exc_info.value.status_code == 401
        call_next.assert_not_called()

    def test_validate_jwt_token_valid(self, auth_middleware, valid_token):
        """Test _validate_jwt_token with valid token."""
        payload = asyncio.run(auth_middleware._validate_jwt_token(valid_token))

        assert payload["sub"] == "user123"
        assert payload["name"] == "Test User"
        assert payload["role"] == "user"
        assert "iat" in payload
        assert "exp" in payload

    def test_validate_jwt_token_expired(self, auth_middleware, expired_token):
        """Test _validate_jwt_token with expired token."""
        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(auth_middleware._validate_jwt_token(expired_token))
        assert "Token has expired" in exc_info.value.detail

    def test_validate_jwt_token_invalid_signature(
        self, auth_middleware, invalid_signature_token
    ):
        """Test _validate_jwt_token with invalid signature."""
        with pytest.raises(HTTPException) as exc_info:
            asyncio.run(auth_middleware._validate_jwt_token(invalid_signature_token))
        assert "Invalid token signature" in exc_info.value.detail

    def test_validate_custom_claims_valid(self, auth_middleware, secret_key):
        """Test _validate_custom_claims with valid payload."""
        payload = {
            "sub": "user123",
            "iat": int(time.time()),
            "exp": int(time.time()) + 3600,
            "name": "Test User",
        }

        # Should not raise any exception
        auth_middleware._validate_custom_claims(payload)

    def test_validate_custom_claims_missing_sub(self, auth_middleware):
        """Test _validate_custom_claims with missing 'sub' claim."""
        payload = {
            "iat": int(time.time()),
            "exp": int(time.time()) + 3600,
            "name": "Test User",
        }

        with pytest.raises(InvalidTokenError, match="Missing required claim: sub"):
            auth_middleware._validate_custom_claims(payload)

    def test_validate_custom_claims_missing_iat(self, auth_middleware):
        """Test _validate_custom_claims with missing 'iat' claim."""
        payload = {
            "sub": "user123",
            "exp": int(time.time()) + 3600,
            "name": "Test User",
        }

        with pytest.raises(InvalidTokenError, match="Missing required claim: iat"):
            auth_middleware._validate_custom_claims(payload)

    def test_verify_token_manually_valid(self, auth_middleware, valid_token):
        """Test verify_token_manually with valid token."""
        result = auth_middleware.verify_token_manually(valid_token)

        assert result is not None
        assert result["sub"] == "user123"
        assert result["name"] == "Test User"

    def test_verify_token_manually_invalid(self, auth_middleware, expired_token):
        """Test verify_token_manually with invalid token."""
        result = auth_middleware.verify_token_manually(expired_token)

        assert result is None

    def test_verify_token_manually_malformed(self, auth_middleware):
        """Test verify_token_manually with malformed token."""
        result = auth_middleware.verify_token_manually("not.a.valid.jwt")

        assert result is None

    @pytest.mark.asyncio
    async def test_dispatch_with_whitespace_token(
        self, auth_middleware, mock_request, valid_token
    ):
        """Test that tokens with whitespace are handled correctly."""
        # Mock request with token that has extra whitespace
        mock_request.headers = {"Authorization": f"Bearer  {valid_token}  "}

        call_next = AsyncMock(return_value="success_response")

        response = await auth_middleware.dispatch(mock_request, call_next)

        assert response == "success_response"
        call_next.assert_called_once_with(mock_request)

    def test_algorithm_configuration(self, secret_key):
        """Test that different algorithms can be configured."""
        middleware_hs256 = AuthMiddleware(secret_key=secret_key, algorithm="HS256")
        middleware_hs512 = AuthMiddleware(secret_key=secret_key, algorithm="HS512")

        assert middleware_hs256.algorithm == "HS256"
        assert middleware_hs512.algorithm == "HS512"

    def test_verification_options_configuration(self, secret_key):
        """Test that verification options can be configured."""
        middleware = AuthMiddleware(
            secret_key=secret_key,
            verify_exp=False,
            verify_aud=True,
            audience="test-audience",
        )

        assert middleware.verify_exp is False
        assert middleware.verify_aud is True
        assert middleware.audience == "test-audience"
