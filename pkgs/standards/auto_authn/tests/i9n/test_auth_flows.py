"""
Integration tests for auto_authn.routers.auth_flows module.

Tests complete authentication flows including registration, login,
logout, token refresh, and API key introspection.
"""

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from auto_authn.orm import Tenant, User, ApiKey
from auto_authn.crypto import hash_pw
from auto_authn.jwtoken import JWTCoder


@pytest.mark.integration
class TestRegistrationFlow:
    """Test user registration endpoint and flow."""

    async def test_register_new_user_success(
        self, async_client: AsyncClient, db_session: AsyncSession
    ):
        """Test successful user registration."""
        # Create a tenant first
        tenant = Tenant(
            slug="test-tenant", name="Test Tenant", email="tenant_test@example.com"
        )
        db_session.add(tenant)
        await db_session.commit()

        registration_data = {
            "tenant_slug": "test-tenant",
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "SecurePassword123!",
        }

        response = await async_client.post("/register", json=registration_data)

        assert response.status_code == status.HTTP_201_CREATED

        response_data = response.json()
        assert "access_token" in response_data
        assert "refresh_token" in response_data
        assert response_data["token_type"] == "bearer"

        # Verify user was created in database
        user = await db_session.scalar(select(User).where(User.username == "newuser"))
        assert user is not None
        assert user.email == "newuser@example.com"
        assert user.tenant_id == tenant.id

    async def test_register_with_invalid_tenant(self, async_client: AsyncClient):
        """Test registration with non-existent tenant."""
        registration_data = {
            "tenant_slug": "nonexistent-tenant",
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "SecurePassword123!",
        }

        response = await async_client.post("/register", json=registration_data)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "tenant not found" in response.json()["detail"]

    async def test_register_duplicate_username(
        self, async_client: AsyncClient, db_session: AsyncSession
    ):
        """Test registration with duplicate username."""
        # Create tenant and existing user
        tenant = Tenant(
            slug="test-tenant", name="Test Tenant", email="tenant_test@example.com"
        )
        db_session.add(tenant)
        await db_session.commit()

        existing_user = User(
            tenant_id=tenant.id,
            username="existinguser",
            email="existing@example.com",
            password_hash=hash_pw("password123"),
        )
        db_session.add(existing_user)
        await db_session.commit()

        registration_data = {
            "tenant_slug": "test-tenant",
            "username": "existinguser",
            "email": "different@example.com",
            "password": "SecurePassword123!",
        }

        response = await async_client.post("/register", json=registration_data)

        assert response.status_code == status.HTTP_409_CONFLICT
        assert "duplicate key" in response.json()["detail"]

    async def test_register_duplicate_email(
        self, async_client: AsyncClient, db_session: AsyncSession
    ):
        """Test registration with duplicate email."""
        # Create tenant and existing user
        tenant = Tenant(
            slug="test-tenant", name="Test Tenant", email="tenant_test@example.com"
        )
        db_session.add(tenant)
        await db_session.commit()

        existing_user = User(
            tenant_id=tenant.id,
            username="existinguser",
            email="duplicate@example.com",
            password_hash=hash_pw("password123"),
        )
        db_session.add(existing_user)
        await db_session.commit()

        registration_data = {
            "tenant_slug": "test-tenant",
            "username": "differentuser",
            "email": "duplicate@example.com",
            "password": "SecurePassword123!",
        }

        response = await async_client.post("/register", json=registration_data)

        assert response.status_code == status.HTTP_409_CONFLICT

    async def test_register_invalid_email_format(
        self, async_client: AsyncClient, db_session: AsyncSession
    ):
        """Test registration with invalid email format."""
        tenant = Tenant(
            slug="test-tenant", name="Test Tenant", email="tenant_test@example.com"
        )
        db_session.add(tenant)
        await db_session.commit()

        registration_data = {
            "tenant_slug": "test-tenant",
            "username": "newuser",
            "email": "invalid-email-format",
            "password": "SecurePassword123!",
        }

        response = await async_client.post("/register", json=registration_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    async def test_register_weak_password(
        self, async_client: AsyncClient, db_session: AsyncSession
    ):
        """Test registration with weak password."""
        tenant = Tenant(
            slug="test-tenant", name="Test Tenant", email="tenant_test@example.com"
        )
        db_session.add(tenant)
        await db_session.commit()

        registration_data = {
            "tenant_slug": "test-tenant",
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "weak",  # Too short
        }

        response = await async_client.post("/register", json=registration_data)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


@pytest.mark.integration
class TestLoginFlow:
    """Test user login endpoint and flow."""

    async def setup_test_user(self, db_session: AsyncSession):
        """Helper to create test tenant and user."""
        tenant = Tenant(
            slug="test-tenant", name="Test Tenant", email="tenant_test@example.com"
        )
        db_session.add(tenant)
        await db_session.commit()

        user = User(
            tenant_id=tenant.id,
            username="testuser",
            email="testuser@example.com",
            password_hash=hash_pw("TestPassword123!"),
        )
        db_session.add(user)
        await db_session.commit()

        return tenant, user

    async def test_login_with_username_password(
        self, async_client: AsyncClient, db_session: AsyncSession
    ):
        """Test successful login with username."""
        tenant, user = await self.setup_test_user(db_session)

        login_data = {"identifier": "testuser", "password": "TestPassword123!"}

        response = await async_client.post("/login", json=login_data)

        assert response.status_code == status.HTTP_200_OK

        response_data = response.json()
        assert "access_token" in response_data
        assert "refresh_token" in response_data
        assert response_data["token_type"] == "bearer"

        # Verify token can be decoded
        jwt_coder = JWTCoder.default()
        access_payload = jwt_coder.decode(response_data["access_token"])
        assert access_payload["sub"] == str(user.id)
        assert access_payload["tid"] == str(tenant.id)

    async def test_login_with_email_password(
        self, async_client: AsyncClient, db_session: AsyncSession
    ):
        """Test successful login with email."""
        tenant, user = await self.setup_test_user(db_session)

        login_data = {
            "identifier": "testuser@example.com",
            "password": "TestPassword123!",
        }

        response = await async_client.post("/login", json=login_data)

        assert response.status_code == status.HTTP_200_OK

        response_data = response.json()
        assert "access_token" in response_data
        assert "refresh_token" in response_data

    async def test_login_with_invalid_credentials(
        self, async_client: AsyncClient, db_session: AsyncSession
    ):
        """Test login with invalid credentials."""
        await self.setup_test_user(db_session)

        login_data = {"identifier": "testuser", "password": "WrongPassword!"}

        response = await async_client.post("/login", json=login_data)

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "invalid credentials" in response.json()["detail"]

    async def test_token_endpoint_form_data(
        self, async_client: AsyncClient, db_session: AsyncSession
    ):
        """Test that /token accepts form-encoded credentials."""
        tenant, user = await self.setup_test_user(db_session)

        form = {"username": "testuser", "password": "TestPassword123!"}

        response = await async_client.post("/token", data=form)

        assert response.status_code == status.HTTP_200_OK

        response_data = response.json()
        assert "access_token" in response_data
        assert "refresh_token" in response_data

    async def test_login_inactive_user(
        self, async_client: AsyncClient, db_session: AsyncSession
    ):
        """Test login with inactive user."""
        tenant, user = await self.setup_test_user(db_session)

        # Deactivate user
        user.is_active = False
        await db_session.commit()

        login_data = {"identifier": "testuser", "password": "TestPassword123!"}

        response = await async_client.post("/login", json=login_data)

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.integration
class TestTokenRefresh:
    """Test token refresh endpoint."""

    async def test_refresh_with_valid_token(
        self, async_client: AsyncClient, db_session: AsyncSession
    ):
        """Test token refresh with valid refresh token."""
        # Create test user and get tokens
        tenant = Tenant(
            slug="test-tenant", name="Test Tenant", email="tenant_test@example.com"
        )
        db_session.add(tenant)
        await db_session.commit()

        user = User(
            tenant_id=tenant.id,
            username="testuser",
            email="testuser@example.com",
            password_hash=hash_pw("TestPassword123!"),
        )
        db_session.add(user)
        await db_session.commit()

        # Get initial tokens
        jwt_coder = JWTCoder.default()
        access_token, refresh_token = jwt_coder.sign_pair(
            sub=str(user.id), tid=str(tenant.id)
        )

        refresh_data = {"refresh_token": refresh_token}

        response = await async_client.post("/token/refresh", json=refresh_data)

        assert response.status_code == status.HTTP_200_OK

        response_data = response.json()
        assert "access_token" in response_data
        assert "refresh_token" in response_data
        assert response_data["token_type"] == "bearer"

        # Verify new tokens are different
        assert response_data["access_token"] != access_token
        assert response_data["refresh_token"] != refresh_token

    async def test_refresh_with_invalid_token(self, async_client: AsyncClient):
        """Test token refresh with invalid token."""
        refresh_data = {"refresh_token": "invalid.token.here"}

        response = await async_client.post("/token/refresh", json=refresh_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "invalid refresh token" in response.json()["detail"]

    async def test_refresh_with_access_token(
        self, async_client: AsyncClient, db_session: AsyncSession
    ):
        """Test token refresh with access token (should fail)."""
        # Create test user and get tokens
        tenant = Tenant(
            slug="test-tenant", name="Test Tenant", email="tenant_test@example.com"
        )
        db_session.add(tenant)
        await db_session.commit()

        user = User(
            tenant_id=tenant.id,
            username="testuser",
            email="testuser@example.com",
            password_hash=hash_pw("TestPassword123!"),
        )
        db_session.add(user)
        await db_session.commit()

        # Get tokens and try to refresh with access token
        jwt_coder = JWTCoder.default()
        access_token, refresh_token = jwt_coder.sign_pair(
            sub=str(user.id), tid=str(tenant.id)
        )

        refresh_data = {"refresh_token": access_token}  # Using access token instead

        response = await async_client.post("/token/refresh", json=refresh_data)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.integration
class TestLogoutEndpoint:
    """Test logout endpoint and session handling."""

    async def test_logout_clears_session_cookie(
        self, async_client: AsyncClient, db_session: AsyncSession
    ):
        """Logging out clears the session cookie and returns 204."""
        tenant = Tenant(slug="logout-tenant", name="LT", email="lt@example.com")
        db_session.add(tenant)
        await db_session.commit()

        user = User(
            tenant_id=tenant.id,
            username="logout-user",
            email="logout@example.com",
            password_hash=hash_pw("TestPassword123!"),
        )
        db_session.add(user)
        await db_session.commit()

        login_data = {"identifier": "logout-user", "password": "TestPassword123!"}
        login_response = await async_client.post("/login", json=login_data)
        assert login_response.status_code == status.HTTP_200_OK
        id_token = login_response.json()["id_token"]
        assert async_client.cookies.get("sid") is not None

        response = await async_client.post("/logout", json={"id_token_hint": id_token})

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert async_client.cookies.get("sid") is None


@pytest.mark.integration
class TestApiKeyIntrospection:
    """Test API key introspection endpoint."""

    async def test_introspect_valid_api_key(
        self, async_client: AsyncClient, db_session: AsyncSession, enable_rfc7662
    ):
        """Test API key introspection with valid key."""
        # Create test tenant and user
        tenant = Tenant(
            slug="test-tenant", name="Test Tenant", email="tenant_test@example.com"
        )
        db_session.add(tenant)
        await db_session.commit()

        user = User(
            tenant_id=tenant.id,
            username="testuser",
            email="testuser@example.com",
            password_hash=hash_pw("TestPassword123!"),
        )
        db_session.add(user)
        await db_session.commit()

        # Create API key
        raw_key = "test-api-key-12345"
        api_key = ApiKey(user_id=user.id, label="Test Key")
        api_key.raw_key = raw_key
        db_session.add(api_key)
        await db_session.commit()

        response = await async_client.post("/introspect", data={"token": raw_key})

        assert response.status_code == status.HTTP_200_OK

        response_data = response.json()
        assert response_data["active"] is True
        assert response_data["sub"] == str(user.id)
        assert response_data["tid"] == str(tenant.id)

    async def test_introspect_invalid_api_key(
        self, async_client: AsyncClient, enable_rfc7662
    ):
        """Test API key introspection with invalid key."""

        response = await async_client.post(
            "/introspect", data={"token": "invalid-api-key"}
        )

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["active"] is False

    async def test_introspect_expired_api_key(
        self, async_client: AsyncClient, db_session: AsyncSession, enable_rfc7662
    ):
        """Test API key introspection with expired key."""
        from datetime import datetime, timezone, timedelta

        # Create test tenant and user
        tenant = Tenant(
            slug="test-tenant", name="Test Tenant", email="tenant_test@example.com"
        )
        db_session.add(tenant)
        await db_session.commit()

        user = User(
            tenant_id=tenant.id,
            username="testuser",
            email="testuser@example.com",
            password_hash=hash_pw("TestPassword123!"),
        )
        db_session.add(user)
        await db_session.commit()

        # Create expired API key
        raw_key = "expired-api-key-12345"
        api_key = ApiKey(
            user_id=user.id,
            label="Expired Key",
            valid_to=datetime.now(timezone.utc) - timedelta(days=1),
        )
        api_key.raw_key = raw_key
        db_session.add(api_key)
        await db_session.commit()

        response = await async_client.post("/introspect", data={"token": raw_key})

        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert response_data["active"] is False


# Test helper functions
@pytest.mark.integration
async def test_authentication_helpers():
    """Test helper functions for authentication testing."""
    from auto_authn.crypto import hash_pw, verify_pw

    password = "TestPassword123!"
    hashed = hash_pw(password)

    assert verify_pw(password, hashed) is True
    assert verify_pw("wrong", hashed) is False
