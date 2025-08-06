"""
Shared test configuration and fixtures for auto_authn test suite.
"""

import asyncio
import os
import tempfile
import uuid
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.pool import StaticPool

from auto_authn.v2.app import app
from auto_authn.v2.db import get_async_db
from auto_authn.v2.orm.tables import Base, Tenant, User, Client, ApiKey
from auto_authn.v2.crypto import _DEFAULT_KEY_PATH, hash_pw


# Test database configuration
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Create an event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def test_db_engine():
    """Create a test database engine."""
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=StaticPool,
        connect_args={"check_same_thread": False},
        echo=False,
    )

    # Create all tables
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Cleanup
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(test_db_engine) -> AsyncGenerator[AsyncSession, None]:
    """Provide a database session for tests."""
    async with AsyncSession(test_db_engine) as session:
        yield session
        await session.rollback()


@pytest.fixture
def override_get_db(db_session):
    """Override the database dependency for testing."""

    async def _get_test_db():
        yield db_session

    app.dependency_overrides[get_async_db] = _get_test_db
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def test_client(override_get_db) -> TestClient:
    """Create a FastAPI test client."""
    return TestClient(app)


@pytest_asyncio.fixture
async def async_client(override_get_db) -> AsyncGenerator[AsyncClient, None]:
    """Create an async HTTP client for testing."""
    from httpx import ASGITransport

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client


@pytest.fixture
def temp_key_file():
    """Create a temporary JWT key file path for testing (file doesn't exist initially)."""
    # Create a temp file path but don't create the file
    temp_dir = Path(tempfile.mkdtemp())
    temp_path = temp_dir / "test_jwt_key.pem"

    # Store original path
    original_path = _DEFAULT_KEY_PATH

    # Monkey patch the key path
    import auto_authn.v2.crypto as crypto_module

    crypto_module._DEFAULT_KEY_PATH = temp_path

    yield temp_path

    # Cleanup
    if temp_path.exists():
        temp_path.unlink()
    if temp_dir.exists():
        temp_dir.rmdir()
    crypto_module._DEFAULT_KEY_PATH = original_path


@pytest.fixture
def mock_env_vars():
    """Mock environment variables for testing."""
    env_vars = {
        "AUTHN_ISSUER": "https://test.example.com",
        "JWT_ED25519_PRIV_PATH": "test_keys/jwt_ed25519.pem",
    }

    original_vars = {}
    for key, value in env_vars.items():
        original_vars[key] = os.environ.get(key)
        os.environ[key] = value

    yield env_vars

    # Restore original values
    for key, original_value in original_vars.items():
        if original_value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = original_value


# =============================================================================
# Sample Data Fixtures and Factories
# =============================================================================


@pytest.fixture
def sample_tenant_data():
    """Sample tenant data for testing."""
    return {
        "slug": "test-tenant",
        "name": "Test Tenant",
    }


@pytest.fixture
def sample_user_data():
    """Sample user data for testing."""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "TestPassword123!",
    }


@pytest.fixture
def sample_client_data():
    """Sample OAuth client data for testing."""
    return {
        "client_id": "test-client-12345",
        "client_secret": "super-secret-client-key",
        "redirect_uris": ["https://app.example.com/callback"],
    }


@pytest.fixture
def sample_api_key_data():
    """Sample API key data for testing."""
    return {
        "label": "Test API Key",
        "raw_key": "test-api-key-12345",
    }


# Database object fixtures
@pytest_asyncio.fixture
async def test_tenant(db_session: AsyncSession):
    """Create a test tenant in the database."""
    tenant = Tenant(slug="test-tenant", name="Test Tenant", is_active=True)
    db_session.add(tenant)
    await db_session.commit()
    return tenant


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession, test_tenant: Tenant):
    """Create a test user in the database."""
    user = User(
        tenant_id=test_tenant.id,
        username="testuser",
        email="testuser@example.com",
        password_hash=hash_pw("TestPassword123!"),
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    return user


@pytest_asyncio.fixture
async def test_client_obj(db_session: AsyncSession, test_tenant: Tenant):
    """Create a test OAuth client in the database."""
    client = Client.new(
        tenant_id=test_tenant.id,
        client_id="test-client-12345",
        client_secret="super-secret-client-key",
        redirects=["https://app.example.com/callback"],
    )
    db_session.add(client)
    await db_session.commit()
    return client


@pytest_asyncio.fixture
async def test_api_key(db_session: AsyncSession, test_user: User):
    """Create a test API key in the database."""
    raw_key = "test-api-key-12345"
    api_key = ApiKey(user_id=test_user.id, label="Test API Key")
    api_key.raw_key = raw_key
    db_session.add(api_key)
    await db_session.commit()
    # Store the raw key for test use
    api_key._test_raw_key = raw_key
    return api_key


@pytest_asyncio.fixture
async def expired_api_key(db_session: AsyncSession, test_user: User):
    """Create an expired API key in the database."""
    raw_key = "expired-api-key-12345"
    api_key = ApiKey(
        user_id=test_user.id,
        label="Expired API Key",
        valid_to=datetime.now(timezone.utc) - timedelta(days=1),
    )
    api_key.raw_key = raw_key
    db_session.add(api_key)
    await db_session.commit()
    api_key._test_raw_key = raw_key
    return api_key


# =============================================================================
# Test Data Factory Classes
# =============================================================================


class MockDataFactory:
    """Factory for generating realistic test data."""

    @staticmethod
    def create_tenant_data(**overrides):
        """Generate tenant data with optional overrides."""
        data = {
            "slug": f"tenant-{uuid.uuid4().hex[:8]}",
            "name": "Test Tenant Corporation",
            "is_active": True,
        }
        data.update(overrides)
        return data

    @staticmethod
    def create_user_data(**overrides):
        """Generate user data with optional overrides."""
        user_id = uuid.uuid4().hex[:8]
        data = {
            "username": f"user{user_id}",
            "email": f"user{user_id}@example.com",
            "password": "SecurePassword123!",
            "is_active": True,
        }
        data.update(overrides)
        return data

    @staticmethod
    def create_client_data(**overrides):
        """Generate OAuth client data with optional overrides."""
        client_id = uuid.uuid4().hex[:12]
        data = {
            "client_id": f"client-{client_id}",
            "client_secret": f"secret-{uuid.uuid4().hex}",
            "redirect_uris": ["https://app.example.com/callback"],
            "is_active": True,
        }
        data.update(overrides)
        return data

    @staticmethod
    def create_api_key_data(**overrides):
        """Generate API key data with optional overrides."""
        key_id = uuid.uuid4().hex[:8]
        data = {
            "label": f"API Key {key_id}",
            "raw_key": f"key-{uuid.uuid4().hex}",
            "is_active": True,
        }
        data.update(overrides)
        return data


@pytest.fixture
def mock_data_factory():
    """Provide the mock data factory."""
    return MockDataFactory


# =============================================================================
# Authentication Test Helpers
# =============================================================================


class AuthTestClient:
    """Enhanced test client with authentication helpers."""

    def __init__(self, client: AsyncClient):
        self.client = client
        self._tokens = {}

    async def register_user(
        self, tenant_slug: str, username: str, email: str, password: str
    ):
        """Helper to register a new user and return tokens."""
        registration_data = {
            "tenant_slug": tenant_slug,
            "username": username,
            "email": email,
            "password": password,
        }

        response = await self.client.post("/register", json=registration_data)
        if response.status_code == 201:
            tokens = response.json()
            self._tokens[username] = tokens
            return tokens
        else:
            response.raise_for_status()

    async def login(self, identifier: str, password: str):
        """Helper to login and return tokens."""
        login_data = {"identifier": identifier, "password": password}

        response = await self.client.post("/login", json=login_data)
        if response.status_code == 200:
            tokens = response.json()
            self._tokens[identifier] = tokens
            return tokens
        else:
            response.raise_for_status()

    async def authenticated_request(
        self, method: str, url: str, user_identifier: str, **kwargs
    ):
        """Make an authenticated request using stored tokens."""
        tokens = self._tokens.get(user_identifier)
        if not tokens:
            raise ValueError(
                f"No tokens found for user {user_identifier}. Login first."
            )

        headers = kwargs.get("headers", {})
        headers["Authorization"] = f"Bearer {tokens['access_token']}"
        kwargs["headers"] = headers

        return await self.client.request(method, url, **kwargs)

    async def introspect_api_key(self, api_key: str):
        """Helper to introspect an API key."""
        introspect_data = {"api_key": api_key}
        return await self.client.post("/api_keys/introspect", json=introspect_data)


@pytest_asyncio.fixture
async def auth_test_client(async_client: AsyncClient):
    """Provide an authentication-enhanced test client."""
    return AuthTestClient(async_client)


# =============================================================================
# Pytest Configuration and Markers
# =============================================================================

# Test markers configuration
pytest_plugins = ["pytest_asyncio"]


# Custom markers
def pytest_configure(config):
    config.addinivalue_line(
        "markers", "unit: Unit tests that test individual functions/classes"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests that test multiple components"
    )
    config.addinivalue_line("markers", "performance: Performance and benchmark tests")
    config.addinivalue_line("markers", "security: Security-focused tests")
    config.addinivalue_line("markers", "slow: Tests that take longer to run")
