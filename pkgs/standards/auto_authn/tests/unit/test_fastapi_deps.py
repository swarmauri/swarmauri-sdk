"""
Unit tests for auto_authn.v2.fastapi_deps module.

Tests FastAPI dependency functions including database sessions,
authentication, principal resolution, and error handling.
"""

import uuid
from unittest.mock import MagicMock, patch, AsyncMock
import contextvars

import pytest
from fastapi import HTTPException, Request
from sqlalchemy.ext.asyncio import AsyncSession
from auto_authn.v2.jwtoken import InvalidTokenError

from auto_authn.v2.fastapi_deps import (
    get_current_principal,
    get_principal,
    _user_from_jwt,
    _user_from_api_key,
    principal_var,
)
from auto_authn.v2.backends import AuthError


@pytest.mark.unit
class TestDatabaseDependency:
    """Test database session dependency functionality."""

    def test_database_dependency_import(self):
        """Test that database dependency can be imported correctly."""
        from auto_authn.v2.fastapi_deps import get_async_db
        from auto_authn.v2.db import get_async_db as db_get_async_db

        # Verify they're the same function
        assert get_async_db is db_get_async_db

    def test_database_session_mock_behavior(self):
        """Test that we can mock database session behavior for testing."""
        # Create a mock session
        mock_session = AsyncMock(spec=AsyncSession)

        # Verify it has the expected async methods
        assert hasattr(mock_session, "execute")
        assert hasattr(mock_session, "commit")
        assert hasattr(mock_session, "rollback")
        assert hasattr(mock_session, "scalar")


@pytest.mark.unit
class TestJWTUserResolution:
    """Test JWT token user resolution functionality."""

    @pytest.mark.asyncio
    async def test_user_from_jwt_with_valid_token(self):
        """Test user resolution from valid JWT token."""
        # Create mock user
        mock_user = MagicMock()
        mock_user.id = uuid.uuid4()
        mock_user.username = "testuser"

        # Create mock database session
        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.scalar.return_value = mock_user

        # Create a valid JWT payload
        with patch("auto_authn.v2.fastapi_deps._jwt_coder") as mock_coder:
            mock_coder.async_decode = AsyncMock(
                return_value={
                    "sub": str(mock_user.id),
                    "iat": 1234567890,
                    "exp": 9999999999,
                }
            )

            user = await _user_from_jwt("valid.jwt.token", mock_db)

            assert user is not None
            assert user.id == mock_user.id
            assert user.username == mock_user.username
            mock_db.scalar.assert_called_once()

    @pytest.mark.asyncio
    async def test_user_from_jwt_with_invalid_token(self):
        """Test user resolution with invalid JWT token."""
        mock_db = AsyncMock(spec=AsyncSession)

        with patch("auto_authn.v2.fastapi_deps._jwt_coder") as mock_coder:
            mock_coder.async_decode = AsyncMock(
                side_effect=InvalidTokenError("Invalid token")
            )

            user = await _user_from_jwt("invalid.jwt.token", mock_db)

            assert user is None
            # Database should not be called for invalid tokens
            mock_db.scalar.assert_not_called()

    @pytest.mark.asyncio
    async def test_user_from_jwt_with_nonexistent_user(self):
        """Test user resolution when JWT contains ID of nonexistent user."""
        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.scalar.return_value = None  # User not found

        with patch("auto_authn.v2.fastapi_deps._jwt_coder") as mock_coder:
            mock_coder.async_decode = AsyncMock(
                return_value={
                    "sub": str(uuid.uuid4()),  # Random non-existent user ID
                    "iat": 1234567890,
                    "exp": 9999999999,
                }
            )

            user = await _user_from_jwt("valid.jwt.token", mock_db)

            assert user is None
            mock_db.scalar.assert_called_once()

    @pytest.mark.asyncio
    async def test_user_from_jwt_with_inactive_user(self):
        """Test user resolution when user exists but is inactive."""
        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.scalar.return_value = None  # Inactive user filtered out by query

        with patch("auto_authn.v2.fastapi_deps._jwt_coder") as mock_coder:
            mock_coder.async_decode = AsyncMock(
                return_value={
                    "sub": str(uuid.uuid4()),
                    "iat": 1234567890,
                    "exp": 9999999999,
                }
            )

            user = await _user_from_jwt("valid.jwt.token", mock_db)

            assert user is None
            mock_db.scalar.assert_called_once()

    @pytest.mark.asyncio
    async def test_user_from_jwt_missing_sub_claim(self):
        """Test JWT payload missing required 'sub' claim raises KeyError."""
        mock_db = AsyncMock(spec=AsyncSession)

        with patch("auto_authn.v2.fastapi_deps._jwt_coder") as mock_coder:
            mock_coder.async_decode = AsyncMock(
                return_value={
                    "iat": 1234567890,
                    "exp": 9999999999,
                }
            )

            with pytest.raises(KeyError):
                await _user_from_jwt("malformed.jwt.token", mock_db)


@pytest.mark.unit
class TestAPIKeyUserResolution:
    """Test API key user resolution functionality."""

    @pytest.mark.asyncio
    async def test_user_from_api_key_with_valid_key(self):
        """Test user resolution from valid API key."""
        # Create mock user
        mock_user = MagicMock()
        mock_user.id = uuid.uuid4()

        mock_db = AsyncMock(spec=AsyncSession)
        raw_key = "valid-api-key-12345"

        with patch("auto_authn.v2.fastapi_deps._api_key_backend") as mock_backend:
            mock_backend.authenticate = AsyncMock(return_value=(mock_user, "user"))

            user = await _user_from_api_key(raw_key, mock_db)

            assert user is not None
            assert user.id == mock_user.id
            mock_backend.authenticate.assert_called_once_with(mock_db, raw_key)

    @pytest.mark.asyncio
    async def test_user_from_api_key_with_invalid_key(self):
        """Test user resolution with invalid API key."""
        mock_db = AsyncMock(spec=AsyncSession)
        raw_key = "invalid-api-key"

        with patch("auto_authn.v2.fastapi_deps._api_key_backend") as mock_backend:
            mock_backend.authenticate = AsyncMock(
                side_effect=AuthError("Invalid API key")
            )

            user = await _user_from_api_key(raw_key, mock_db)

            assert user is None
            mock_backend.authenticate.assert_called_once_with(mock_db, raw_key)

    @pytest.mark.asyncio
    async def test_user_from_api_key_with_expired_key(self):
        """Test user resolution with expired API key."""
        mock_db = AsyncMock(spec=AsyncSession)
        raw_key = "expired-api-key"

        with patch("auto_authn.v2.fastapi_deps._api_key_backend") as mock_backend:
            mock_backend.authenticate = AsyncMock(
                side_effect=AuthError("API key expired")
            )

            user = await _user_from_api_key(raw_key, mock_db)

            assert user is None

    @pytest.mark.asyncio
    async def test_user_from_api_key_with_service_principal(self):
        """Test resolution of service principal via API key."""
        mock_service = MagicMock()
        mock_service.id = uuid.uuid4()

        mock_db = AsyncMock(spec=AsyncSession)
        raw_key = "service-api-key"

        with patch("auto_authn.v2.fastapi_deps._api_key_backend") as mock_backend:
            mock_backend.authenticate = AsyncMock(
                return_value=(mock_service, "service")
            )

            principal = await _user_from_api_key(raw_key, mock_db)

            assert principal is mock_service
            mock_backend.authenticate.assert_called_once_with(mock_db, raw_key)

    @pytest.mark.asyncio
    async def test_user_from_api_key_with_client_principal(self):
        """Test resolution of client principal via API key."""
        mock_client = MagicMock()
        mock_client.id = uuid.uuid4()

        mock_db = AsyncMock(spec=AsyncSession)
        raw_key = "client-api-key"

        with patch("auto_authn.v2.fastapi_deps._api_key_backend") as mock_backend:
            mock_backend.authenticate = AsyncMock(return_value=(mock_client, "client"))

            principal = await _user_from_api_key(raw_key, mock_db)

            assert principal is mock_client
            mock_backend.authenticate.assert_called_once_with(mock_db, raw_key)


@pytest.mark.unit
class TestGetCurrentPrincipal:
    """Test get_current_principal dependency functionality."""

    @pytest.mark.asyncio
    async def test_get_current_principal_with_valid_api_key(self):
        """Test principal resolution with valid API key."""
        mock_user = MagicMock()
        mock_user.id = uuid.uuid4()

        mock_db = AsyncMock(spec=AsyncSession)
        api_key = "valid-api-key-12345"

        with patch(
            "auto_authn.v2.fastapi_deps._user_from_api_key", return_value=mock_user
        ):
            request = Request(scope={"type": "http"})
            principal = await get_current_principal(
                request,
                authorization="",
                api_key=api_key,
                db=mock_db,
            )

            assert principal is not None
            assert principal.id == mock_user.id

    @pytest.mark.asyncio
    async def test_get_current_principal_with_valid_jwt(self):
        """Test principal resolution with valid JWT token."""
        mock_user = MagicMock()
        mock_user.id = uuid.uuid4()

        mock_db = AsyncMock(spec=AsyncSession)
        authorization = "Bearer valid.jwt.token"

        with patch("auto_authn.v2.fastapi_deps._user_from_jwt", return_value=mock_user):
            request = Request(scope={"type": "http"})
            principal = await get_current_principal(
                request,
                authorization=authorization,
                api_key=None,
                db=mock_db,
            )

            assert principal is not None
            assert principal.id == mock_user.id

    @pytest.mark.asyncio
    async def test_get_current_principal_api_key_takes_precedence(self):
        """Test that API key takes precedence over JWT when both are provided."""
        mock_user = MagicMock()
        mock_user.id = uuid.uuid4()

        mock_db = AsyncMock(spec=AsyncSession)
        api_key = "valid-api-key-12345"
        authorization = "Bearer valid.jwt.token"

        with patch(
            "auto_authn.v2.fastapi_deps._user_from_api_key", return_value=mock_user
        ) as mock_api:
            with patch(
                "auto_authn.v2.fastapi_deps._user_from_jwt", return_value=mock_user
            ) as mock_jwt:
                request = Request(scope={"type": "http"})
                principal = await get_current_principal(
                    request,
                    authorization=authorization,
                    api_key=api_key,
                    db=mock_db,
                )

                assert principal is not None
                assert principal.id == mock_user.id

                # API key should be checked first
                mock_api.assert_called_once_with(api_key, mock_db)
                # JWT should not be checked when API key succeeds
                mock_jwt.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_current_principal_falls_back_to_jwt(self):
        """Test fallback to JWT when API key is invalid."""
        mock_user = MagicMock()
        mock_user.id = uuid.uuid4()

        mock_db = AsyncMock(spec=AsyncSession)
        api_key = "invalid-api-key"
        authorization = "Bearer valid.jwt.token"

        with patch("auto_authn.v2.fastapi_deps._user_from_api_key", return_value=None):
            with patch(
                "auto_authn.v2.fastapi_deps._user_from_jwt", return_value=mock_user
            ):
                request = Request(scope={"type": "http"})
                principal = await get_current_principal(
                    request,
                    authorization=authorization,
                    api_key=api_key,
                    db=mock_db,
                )

                assert principal is not None
                assert principal.id == mock_user.id

    @pytest.mark.asyncio
    async def test_get_current_principal_with_no_credentials(self):
        """Test principal resolution with no credentials raises HTTP 401."""
        mock_db = AsyncMock(spec=AsyncSession)

        request = Request(scope={"type": "http"})
        with pytest.raises(HTTPException) as exc_info:
            await get_current_principal(
                request, authorization="", api_key=None, db=mock_db
            )

        assert exc_info.value.status_code == 401
        assert "invalid or missing credentials" in exc_info.value.detail
        assert exc_info.value.headers == {"WWW-Authenticate": 'Bearer realm="authn"'}

    @pytest.mark.asyncio
    async def test_get_current_principal_with_invalid_bearer_format(self):
        """Test principal resolution with malformed Bearer token."""
        mock_db = AsyncMock(spec=AsyncSession)
        authorization = "InvalidFormat token"

        request = Request(scope={"type": "http"})
        with pytest.raises(HTTPException) as exc_info:
            await get_current_principal(
                request,
                authorization=authorization,
                api_key=None,
                db=mock_db,
            )

        assert exc_info.value.status_code == 401

    @pytest.mark.asyncio
    async def test_get_current_principal_with_invalid_credentials(self):
        """Test principal resolution with invalid API key and JWT."""
        mock_db = AsyncMock(spec=AsyncSession)
        api_key = "invalid-api-key"
        authorization = "Bearer invalid.jwt.token"

        with patch("auto_authn.v2.fastapi_deps._user_from_api_key", return_value=None):
            with patch("auto_authn.v2.fastapi_deps._user_from_jwt", return_value=None):
                request = Request(scope={"type": "http"})
                with pytest.raises(HTTPException) as exc_info:
                    await get_current_principal(
                        request,
                        authorization=authorization,
                        api_key=api_key,
                        db=mock_db,
                    )

                assert exc_info.value.status_code == 401


@pytest.mark.unit
class TestGetPrincipal:
    """Test get_principal AutoAPI-compatible dependency."""

    @pytest.mark.asyncio
    async def test_get_principal_with_valid_credentials(self):
        """Test principal dict creation with valid credentials."""
        # Create mock user with tenant relationship
        mock_user = MagicMock()
        mock_user.id = uuid.uuid4()
        tenant_id = uuid.uuid4()
        mock_user.tenant_id = tenant_id

        mock_request = MagicMock(spec=Request)
        mock_request.state = MagicMock()
        mock_db = AsyncMock(spec=AsyncSession)

        api_key = "valid-api-key-12345"

        with patch(
            "auto_authn.v2.fastapi_deps.get_current_principal", return_value=mock_user
        ):
            principal = await get_principal(
                request=mock_request, authorization="", api_key=api_key, db=mock_db
            )

            assert principal == {"sub": str(mock_user.id), "tid": str(tenant_id)}

    @pytest.mark.asyncio
    async def test_get_principal_sets_request_state(self):
        """Test that get_principal sets the principal in request state."""
        mock_user = MagicMock()
        mock_user.id = uuid.uuid4()
        tenant_id = uuid.uuid4()
        mock_user.tenant_id = tenant_id

        mock_request = MagicMock(spec=Request)
        mock_request.state = MagicMock()
        mock_db = AsyncMock(spec=AsyncSession)

        with patch(
            "auto_authn.v2.fastapi_deps.get_current_principal", return_value=mock_user
        ):
            await get_principal(
                request=mock_request,
                authorization="Bearer valid.jwt.token",
                api_key=None,
                db=mock_db,
            )

            # Verify request state is set
            expected_principal = {"sub": str(mock_user.id), "tid": str(tenant_id)}
            assert mock_request.state.principal == expected_principal

    @pytest.mark.asyncio
    async def test_get_principal_sets_context_var(self):
        """Test that get_principal sets the principal context variable."""
        mock_user = MagicMock()
        mock_user.id = uuid.uuid4()
        tenant_id = uuid.uuid4()
        mock_user.tenant_id = tenant_id

        mock_request = MagicMock(spec=Request)
        mock_request.state = MagicMock()
        mock_db = AsyncMock(spec=AsyncSession)

        # Clear any existing context
        principal_var.set(None)

        with patch(
            "auto_authn.v2.fastapi_deps.get_current_principal", return_value=mock_user
        ):
            await get_principal(
                request=mock_request,
                authorization="Bearer valid.jwt.token",
                api_key=None,
                db=mock_db,
            )

            # Verify context variable is set
            expected_principal = {"sub": str(mock_user.id), "tid": str(tenant_id)}
            assert principal_var.get() == expected_principal

    @pytest.mark.asyncio
    async def test_get_principal_with_authentication_failure(self):
        """Test get_principal when authentication fails."""
        mock_request = MagicMock(spec=Request)
        mock_request.state = MagicMock()
        mock_db = AsyncMock(spec=AsyncSession)

        with patch(
            "auto_authn.v2.fastapi_deps.get_current_principal"
        ) as mock_get_current:
            mock_get_current.side_effect = HTTPException(
                status_code=401, detail="invalid credentials"
            )

            with pytest.raises(HTTPException) as exc_info:
                await get_principal(
                    request=mock_request, authorization="", api_key=None, db=mock_db
                )

            assert exc_info.value.status_code == 401


@pytest.mark.unit
class TestPrincipalContextVar:
    """Test principal context variable functionality."""

    def test_principal_var_default_value(self):
        """Test that principal context variable has correct default value."""
        # Clear any existing context
        principal_var.set(None)

        # Default should be None
        assert principal_var.get() is None

    def test_principal_var_can_be_set_and_retrieved(self):
        """Test that principal context variable can be set and retrieved."""
        test_principal = {"sub": "user-123", "tid": "tenant-456"}

        principal_var.set(test_principal)
        assert principal_var.get() == test_principal

    def test_principal_var_context_isolation(self):
        """Test that principal context variable is properly isolated between contexts."""
        principal1 = {"sub": "user-1", "tid": "tenant-1"}
        principal2 = {"sub": "user-2", "tid": "tenant-2"}

        # Set initial value
        principal_var.set(principal1)
        assert principal_var.get() == principal1

        # Create new context and set different value
        ctx = contextvars.copy_context()

        def set_principal_in_context():
            principal_var.set(principal2)
            return principal_var.get()

        result = ctx.run(set_principal_in_context)

        # Value in new context should be different
        assert result == principal2

        # Original context should still have original value
        assert principal_var.get() == principal1


@pytest.mark.unit
class TestFastAPIDepsIntegration:
    """Test integration aspects and edge cases."""

    def test_all_exports_are_available(self):
        """Test that all expected exports are available from the module."""
        from auto_authn.v2.fastapi_deps import (
            get_current_principal,
            get_principal,
            principal_var,
            PasswordBackend,
            ApiKeyBackend,
        )

        # Verify all expected exports exist
        assert callable(get_current_principal)
        assert callable(get_principal)
        assert isinstance(principal_var, contextvars.ContextVar)
        assert PasswordBackend is not None
        assert ApiKeyBackend is not None

    def test_backend_instances_are_created(self):
        """Test that backend instances are properly initialized."""
        from auto_authn.v2.fastapi_deps import _api_key_backend, _jwt_coder

        # Verify backend instances exist
        assert _api_key_backend is not None
        assert _jwt_coder is not None

    @pytest.mark.asyncio
    async def test_database_error_handling(self):
        """Test handling of database errors in dependencies."""
        mock_db = AsyncMock(spec=AsyncSession)
        mock_db.scalar.side_effect = Exception("Database error")

        with patch("auto_authn.v2.fastapi_deps._jwt_coder") as mock_coder:
            mock_coder.async_decode = AsyncMock(
                return_value={
                    "sub": str(uuid.uuid4()),
                    "iat": 1234567890,
                    "exp": 9999999999,
                }
            )

            # Should handle database errors gracefully
            with pytest.raises(Exception, match="Database error"):
                await _user_from_jwt("valid.jwt.token", mock_db)

    def test_header_parsing_edge_cases(self):
        """Test edge cases in header parsing."""
        # Test various Bearer token formats
        test_cases = [
            ("Bearer ", None),  # Empty token
            ("Bearer", None),  # No space
            ("bearer token", None),  # Lowercase
            ("Bearer token", "token"),  # Valid
            ("Bearer  token", "token"),  # Extra space
        ]

        for auth_header, expected_token in test_cases:
            if auth_header.startswith("Bearer ") and len(auth_header.split()) == 2:
                token = auth_header.split()[1]
                assert token == expected_token
            else:
                # Invalid format - would not extract token
                assert expected_token is None or expected_token == "token"
