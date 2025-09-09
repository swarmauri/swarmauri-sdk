"""
Unit tests for tigrbl_auth.backends module.

Tests authentication backends for password and API key authentication.
"""

from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

from tigrbl_auth.backends import AuthError, PasswordBackend, ApiKeyBackend
from tigrbl_auth.crypto import hash_pw
from tigrbl_auth.orm import User, ApiKey, ServiceKey, Service


@pytest.mark.unit
class TestAuthError:
    """Test AuthError exception class."""

    def test_auth_error_default_message(self):
        """Test AuthError with default message."""
        error = AuthError()
        assert str(error) == "authentication failed"
        assert error.reason == "authentication failed"

    def test_auth_error_custom_message(self):
        """Test AuthError with custom message."""
        custom_message = "invalid credentials"
        error = AuthError(custom_message)
        assert str(error) == custom_message
        assert error.reason == custom_message

    def test_auth_error_inheritance(self):
        """Test that AuthError inherits from Exception."""
        error = AuthError()
        assert isinstance(error, Exception)


@pytest.mark.unit
class TestPasswordBackend:
    """Test password authentication backend."""

    def setup_method(self):
        """Set up test fixtures for each test method."""
        self.backend = PasswordBackend()
        self.mock_db = AsyncMock()

    def create_mock_user(self, mock_data_factory, **overrides):
        """Create a mock user using data factory for consistency."""
        user_data = mock_data_factory.create_user_data(**overrides)
        user = MagicMock(spec=User)
        user.id = uuid4()
        user.username = user_data["username"]
        user.email = user_data["email"]
        user.password_hash = (
            hash_pw(user_data["password"]) if user_data.get("password") else None
        )
        user.is_active = user_data["is_active"]
        user.tenant_id = uuid4()
        return user

    @pytest.mark.asyncio
    async def test_authenticate_with_valid_username_password(self, mock_data_factory):
        """Test successful authentication with username."""
        mock_user = self.create_mock_user(mock_data_factory)
        self.mock_db.scalar.return_value = mock_user

        # Use the password from the mock user creation
        test_password = "SecurePassword123!"  # Default from factory
        result = await self.backend.authenticate(
            self.mock_db, mock_user.username, test_password
        )

        assert result == mock_user
        self.mock_db.scalar.assert_called_once()

    @pytest.mark.asyncio
    async def test_authenticate_with_valid_email_password(self, mock_data_factory):
        """Test successful authentication with email."""
        mock_user = self.create_mock_user(mock_data_factory)
        self.mock_db.scalar.return_value = mock_user

        test_password = "SecurePassword123!"
        result = await self.backend.authenticate(
            self.mock_db, mock_user.email, test_password
        )

        assert result == mock_user
        self.mock_db.scalar.assert_called_once()

    @pytest.mark.asyncio
    async def test_authenticate_with_invalid_credentials(self, mock_data_factory):
        """Test authentication with invalid password."""
        mock_user = self.create_mock_user(mock_data_factory)
        self.mock_db.scalar.return_value = mock_user

        # Test authentication with wrong password
        with pytest.raises(AuthError) as exc_info:
            await self.backend.authenticate(
                self.mock_db, mock_user.username, "WrongPassword!"
            )

        assert exc_info.value.reason == "invalid username/email or password"

    @pytest.mark.asyncio
    async def test_authenticate_with_nonexistent_user(self):
        """Test authentication with nonexistent user."""
        # Mock database returns None (user not found)
        self.mock_db.scalar.return_value = None

        # Test authentication
        with pytest.raises(AuthError) as exc_info:
            await self.backend.authenticate(self.mock_db, "nonexistent", "password")

        assert exc_info.value.reason == "invalid username/email or password"

    @pytest.mark.asyncio
    async def test_authenticate_with_inactive_user(self):
        """Test authentication with inactive user."""
        # Mock the _get_user_stmt to simulate the query filtering out inactive users
        self.mock_db.scalar.return_value = None  # Inactive users won't be returned

        # Test authentication
        with pytest.raises(AuthError) as exc_info:
            await self.backend.authenticate(
                self.mock_db, "testuser", "TestPassword123!"
            )

        assert exc_info.value.reason == "invalid username/email or password"

    @pytest.mark.asyncio
    async def test_authenticate_with_none_password_hash(self, mock_data_factory):
        """Test authentication when user has no password hash."""
        # Create mock user with None password hash
        mock_user = self.create_mock_user(mock_data_factory, password=None)
        mock_user.password_hash = None
        self.mock_db.scalar.return_value = mock_user

        # Test authentication
        with pytest.raises(AuthError) as exc_info:
            await self.backend.authenticate(
                self.mock_db, mock_user.username, "TestPassword123!"
            )

        assert exc_info.value.reason == "invalid username/email or password"

    @pytest.mark.asyncio
    async def test_get_user_stmt_structure(self):
        """Test that _get_user_stmt creates correct query structure."""
        stmt = await self.backend._get_user_stmt("testuser")

        # Verify the statement has expected WHERE criteria without compiling
        clauses = list(stmt._where_criteria)
        assert len(clauses) == 2

        # First clause should match username or email
        or_clause = clauses[0]
        sub_keys = {c.left.key for c in or_clause.clauses}
        assert {"username", "email"} <= sub_keys

        # Second clause should ensure the user is active
        assert clauses[1].left.key == "is_active"

    @pytest.mark.asyncio
    async def test_authenticate_with_empty_identifier(self):
        """Test authentication with empty identifier."""
        self.mock_db.scalar.return_value = None

        with pytest.raises(AuthError) as exc_info:
            await self.backend.authenticate(self.mock_db, "", "password")

        assert exc_info.value.reason == "invalid username/email or password"

    @pytest.mark.asyncio
    async def test_authenticate_with_empty_password(self, mock_data_factory):
        """Test authentication with empty password."""
        mock_user = self.create_mock_user(mock_data_factory)
        self.mock_db.scalar.return_value = mock_user

        with pytest.raises(AuthError) as exc_info:
            await self.backend.authenticate(self.mock_db, mock_user.username, "")

        assert exc_info.value.reason == "invalid username/email or password"


@pytest.mark.unit
class TestApiKeyBackend:
    """Test API key authentication backend."""

    def setup_method(self):
        """Set up test fixtures for each test method."""
        self.backend = ApiKeyBackend()
        self.mock_db = AsyncMock()

    def create_mock_user(self, mock_data_factory, **overrides):
        """Create a mock user using data factory for consistency."""
        user_data = mock_data_factory.create_user_data(**overrides)
        user = MagicMock(spec=User)
        user.id = uuid4()
        user.username = user_data["username"]
        user.email = user_data["email"]
        user.is_active = user_data["is_active"]
        user.tenant_id = uuid4()
        return user

    def create_mock_service(self, mock_data_factory, **overrides):
        """Create a mock service using data factory patterns."""
        service_data = {"name": f"service-{uuid4().hex[:8]}", "is_active": True}
        service_data.update(overrides)

        service = MagicMock(spec=Service)
        service.id = uuid4()
        service.name = service_data["name"]
        service.is_active = service_data["is_active"]
        service.tenant_id = uuid4()
        return service

    def create_mock_api_key(
        self, mock_data_factory, user=None, raw_key=None, **overrides
    ):
        """Create a mock API key using data factory patterns."""
        if raw_key is None:
            api_key_data = mock_data_factory.create_api_key_data(**overrides)
            raw_key = api_key_data["raw_key"]

        api_key = MagicMock(spec=ApiKey)
        api_key.id = uuid4()
        api_key.user = user or self.create_mock_user(mock_data_factory)
        api_key.label = f"Test API Key {uuid4().hex[:8]}"
        api_key.digest = ApiKey.digest_of(raw_key)
        api_key.valid_to = overrides.get("valid_to")
        api_key.touch = MagicMock()
        return api_key

    def create_mock_service_key(
        self, mock_data_factory, service=None, raw_key=None, **overrides
    ):
        """Create a mock service key using data factory patterns."""
        if raw_key is None:
            raw_key = f"service-key-{uuid4().hex[:8]}"

        service_key = MagicMock(spec=ServiceKey)
        service_key.id = uuid4()
        service_key.service = service or self.create_mock_service(mock_data_factory)
        service_key.label = f"Test Service Key {uuid4().hex[:8]}"
        service_key.digest = ServiceKey.digest_of(raw_key)
        service_key.valid_to = overrides.get("valid_to")
        service_key.touch = MagicMock()
        return service_key

    def create_mock_client(self, mock_data_factory, **overrides):
        """Create a Client instance with hashed secret."""
        client_data = mock_data_factory.create_client_data(**overrides)
        client_secret = client_data["client_secret"]
        client = MagicMock()
        client.is_active = client_data["is_active"]
        client.verify_secret = MagicMock(side_effect=lambda s: s == client_secret)
        return client, client_secret

    @pytest.mark.asyncio
    async def test_authenticate_with_valid_api_key(self, mock_data_factory):
        """Test successful authentication with valid API key."""
        api_key_data = mock_data_factory.create_api_key_data()
        raw_key = api_key_data["raw_key"]

        mock_user = self.create_mock_user(mock_data_factory)
        mock_api_key = self.create_mock_api_key(
            mock_data_factory, user=mock_user, raw_key=raw_key
        )

        # Mock database to return the API key on first call, None on second
        self.mock_db.scalar.side_effect = [mock_api_key, None]

        principal, key_type = await self.backend.authenticate(self.mock_db, raw_key)

        assert principal == mock_user
        assert key_type == "user"
        mock_api_key.touch.assert_called_once()
        assert self.mock_db.scalar.call_count == 1  # Only user key query needed

    @pytest.mark.asyncio
    async def test_authenticate_with_valid_service_key(self, mock_data_factory):
        """Test successful authentication with valid service key."""
        raw_key = f"service-key-{uuid4().hex[:8]}"
        mock_service = self.create_mock_service(mock_data_factory)
        mock_service_key = self.create_mock_service_key(
            mock_data_factory, service=mock_service, raw_key=raw_key
        )

        # Mock database to return None for user key, service key on second call
        self.mock_db.scalar.side_effect = [None, mock_service_key]

        principal, key_type = await self.backend.authenticate(self.mock_db, raw_key)

        assert principal == mock_service
        assert key_type == "service"
        mock_service_key.touch.assert_called_once()
        assert self.mock_db.scalar.call_count == 2  # Both queries needed

    @pytest.mark.asyncio
    async def test_authenticate_with_invalid_api_key(self):
        """Test authentication with invalid API key."""
        # Mock database returns None for both queries
        self.mock_db.scalar.side_effect = [None, None]

        with pytest.raises(AuthError) as exc_info:
            await self.backend.authenticate(self.mock_db, "invalid-key")

        assert exc_info.value.reason == "API key invalid, revoked, or expired"
        assert self.mock_db.scalar.call_count == 2  # Both queries attempted

    @pytest.mark.asyncio
    async def test_authenticate_with_expired_api_key(self):
        """Test authentication with expired API key."""
        raw_key = "expired-api-key-12345"

        # Create expired API key - but the query should filter it out
        # So mock returns None (expired keys filtered by query)
        self.mock_db.scalar.side_effect = [None, None]

        with pytest.raises(AuthError) as exc_info:
            await self.backend.authenticate(self.mock_db, raw_key)

        assert exc_info.value.reason == "API key invalid, revoked, or expired"

    @pytest.mark.asyncio
    async def test_authenticate_with_inactive_user(self, mock_data_factory):
        """Test authentication with API key for inactive user."""
        api_key_data = mock_data_factory.create_api_key_data()
        raw_key = api_key_data["raw_key"]

        mock_user = self.create_mock_user(mock_data_factory, is_active=False)
        mock_api_key = self.create_mock_api_key(
            mock_data_factory, user=mock_user, raw_key=raw_key
        )

        self.mock_db.scalar.side_effect = [mock_api_key, None]

        with pytest.raises(AuthError) as exc_info:
            await self.backend.authenticate(self.mock_db, raw_key)

        assert exc_info.value.reason == "user is inactive"
        # touch should not be called for inactive users
        mock_api_key.touch.assert_not_called()

    @pytest.mark.asyncio
    async def test_authenticate_with_inactive_service(self, mock_data_factory):
        """Test authentication with service key for inactive service."""
        raw_key = f"service-key-{uuid4().hex[:8]}"
        mock_service = self.create_mock_service(mock_data_factory, is_active=False)
        mock_service_key = self.create_mock_service_key(
            mock_data_factory, service=mock_service, raw_key=raw_key
        )

        self.mock_db.scalar.side_effect = [None, mock_service_key]

        with pytest.raises(AuthError) as exc_info:
            await self.backend.authenticate(self.mock_db, raw_key)

        assert exc_info.value.reason == "service is inactive"
        # touch should not be called for inactive services
        mock_service_key.touch.assert_not_called()

    @pytest.mark.asyncio
    async def test_key_last_used_timestamp_updated(self, mock_data_factory):
        """Test that API key last_used timestamp is updated via touch()."""
        api_key_data = mock_data_factory.create_api_key_data()
        raw_key = api_key_data["raw_key"]

        mock_user = self.create_mock_user(mock_data_factory)
        mock_api_key = self.create_mock_api_key(
            mock_data_factory, user=mock_user, raw_key=raw_key
        )

        self.mock_db.scalar.side_effect = [mock_api_key, None]

        await self.backend.authenticate(self.mock_db, raw_key)

        # Verify touch was called to update last_used timestamp
        mock_api_key.touch.assert_called_once()

    @pytest.mark.asyncio
    async def test_service_key_last_used_timestamp_updated(self, mock_data_factory):
        """Test that service key last_used timestamp is updated via touch()."""
        raw_key = f"service-key-{uuid4().hex[:8]}"
        mock_service = self.create_mock_service(mock_data_factory)
        mock_service_key = self.create_mock_service_key(
            mock_data_factory, service=mock_service, raw_key=raw_key
        )

        self.mock_db.scalar.side_effect = [None, mock_service_key]

        await self.backend.authenticate(self.mock_db, raw_key)

        # Verify touch was called to update last_used timestamp
        mock_service_key.touch.assert_called_once()

    @pytest.mark.asyncio
    async def test_authenticate_with_valid_client_key(self, mock_data_factory):
        """Authenticate using a Client's API key."""
        client, raw_secret = self.create_mock_client(mock_data_factory)
        self.mock_db.scalar.side_effect = [None, None]
        self.mock_db.scalars = AsyncMock(return_value=[client])
        self.backend._get_key_stmt = AsyncMock()
        self.backend._get_service_key_stmt = AsyncMock()
        client.verify_secret = MagicMock(wraps=client.verify_secret)

        with patch("tigrbl_auth.backends._ApiKey") as mock_api_key:
            mock_api_key.return_value.digest_of.return_value = "mock-digest"
            principal, key_type = await self.backend.authenticate(
                self.mock_db, raw_secret
            )

        assert principal == client
        assert key_type == "client"
        client.verify_secret.assert_called_once_with(raw_secret)
        self.mock_db.scalars.assert_called_once()

    @pytest.mark.asyncio
    async def test_authenticate_with_invalid_client_secret(self, mock_data_factory):
        """Invalid secret for a Client should raise AuthError."""
        client, raw_secret = self.create_mock_client(mock_data_factory)
        self.mock_db.scalar.side_effect = [None, None]
        self.mock_db.scalars = AsyncMock(return_value=[client])
        self.backend._get_key_stmt = AsyncMock()
        self.backend._get_service_key_stmt = AsyncMock()
        client.verify_secret = MagicMock(wraps=client.verify_secret)

        with patch("tigrbl_auth.backends._ApiKey") as mock_api_key:
            mock_api_key.return_value.digest_of.return_value = "mock-digest"
            with pytest.raises(AuthError) as exc_info:
                await self.backend.authenticate(self.mock_db, "wrong-secret")

        assert exc_info.value.reason == "API key invalid, revoked, or expired"
        client.verify_secret.assert_called_once_with("wrong-secret")

    @pytest.mark.asyncio
    async def test_authenticate_with_inactive_client(self, mock_data_factory):
        """Inactive clients should not authenticate."""
        client, raw_secret = self.create_mock_client(mock_data_factory, is_active=False)
        self.mock_db.scalar.side_effect = [None, None]
        self.mock_db.scalars = AsyncMock(return_value=[])
        self.backend._get_key_stmt = AsyncMock()
        self.backend._get_service_key_stmt = AsyncMock()

        with patch("tigrbl_auth.backends._ApiKey") as mock_api_key:
            mock_api_key.return_value.digest_of.return_value = "mock-digest"
            with pytest.raises(AuthError) as exc_info:
                await self.backend.authenticate(self.mock_db, raw_secret)

        assert exc_info.value.reason == "API key invalid, revoked, or expired"
        self.mock_db.scalars.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_client_stmt_filters_inactive_clients(self):
        """_get_client_stmt should select only active clients."""
        stmt = await self.backend._get_client_stmt()
        clause = list(stmt._where_criteria)[0]
        assert clause.left.key == "is_active"

    @pytest.mark.asyncio
    async def test_get_key_stmt_filters_expired_keys(self):
        """Test that _get_key_stmt properly filters expired keys."""
        test_digest = "test-digest"

        stmt = await self.backend._get_key_stmt(test_digest)

        clauses = list(stmt._where_criteria)
        assert clauses[0].left.key == "digest"
        sub_keys = {c.left.key for c in clauses[1].clauses}
        assert "valid_to" in sub_keys

    @pytest.mark.asyncio
    async def test_get_service_key_stmt_filters_expired_keys(self):
        """Test that _get_service_key_stmt properly filters expired keys."""
        test_digest = "test-digest"

        stmt = await self.backend._get_service_key_stmt(test_digest)

        clauses = list(stmt._where_criteria)
        assert clauses[0].left.key == "digest"
        sub_keys = {c.left.key for c in clauses[1].clauses}
        assert "valid_to" in sub_keys

    @pytest.mark.asyncio
    async def test_authenticate_with_empty_api_key(self):
        """Test authentication with empty API key."""
        self.mock_db.scalar.side_effect = [None, None]

        with pytest.raises(AuthError) as exc_info:
            await self.backend.authenticate(self.mock_db, "")

        assert exc_info.value.reason == "API key invalid, revoked, or expired"

    @patch("tigrbl_auth.backends._ApiKey")
    @pytest.mark.asyncio
    async def test_digest_of_called_correctly(self, mock_api_key):
        """Test that ApiKey.digest_of is called with the raw key."""
        raw_key = "test-api-key-12345"
        mock_api_key.return_value.digest_of.return_value = "mocked-digest"
        self.mock_db.scalar.side_effect = [None, None]
        self.backend._get_key_stmt = AsyncMock()
        self.backend._get_service_key_stmt = AsyncMock()

        try:
            await self.backend.authenticate(self.mock_db, raw_key)
        except AuthError:
            pass  # Expected

        mock_api_key.return_value.digest_of.assert_called_once_with(raw_key)


@pytest.mark.unit
class TestBackendIntegration:
    """Integration tests for backend components working together."""

    @pytest.mark.asyncio
    async def test_password_and_api_key_backends_work_independently(self):
        """Test that both backends can be used independently."""
        password_backend = PasswordBackend()
        api_key_backend = ApiKeyBackend()

        # Verify they are different instances
        assert password_backend is not api_key_backend
        assert isinstance(password_backend, PasswordBackend)
        assert isinstance(api_key_backend, ApiKeyBackend)

        # Verify they have different methods
        assert hasattr(password_backend, "authenticate")
        assert hasattr(api_key_backend, "authenticate")
        assert hasattr(password_backend, "_get_user_stmt")
        assert hasattr(api_key_backend, "_get_key_stmt")
        assert hasattr(api_key_backend, "_get_service_key_stmt")

    def test_auth_error_consistency(self):
        """Test that AuthError is consistent across backends."""
        # Both backends should raise the same AuthError type
        error1 = AuthError("password error")
        error2 = AuthError("api key error")

        assert isinstance(error1, type(error2))
        assert isinstance(error1, AuthError)
        assert isinstance(error2, AuthError)
