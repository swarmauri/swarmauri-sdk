"""
Shared test configuration and fixtures for tigrbl_auth test suite.
"""

import asyncio
import os
import shutil
import tempfile
import uuid
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from fastapi.testclient import TestClient
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from tigrbl_auth.app import app
from tigrbl_auth.db import get_db
from tigrbl_auth.routers.surface import surface_api
from tigrbl_auth.orm import Base, Tenant, User, Client, ApiKey
from tigrbl_auth.crypto import hash_pw
from autoapi.v3.engine import resolver as engine_resolver
from autoapi.v3.engine.engine_spec import EngineSpec
from autoapi.v3.engine._engine import Provider


# Disable TLS enforcement for tests
@pytest.fixture(autouse=True)
def disable_tls_requirement():
    from tigrbl_auth.runtime_cfg import settings

    original = settings.require_tls
    settings.require_tls = False
    try:
        yield
    finally:
        settings.require_tls = original


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
        execution_options={"schema_translate_map": {"authn": None}},
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
def override_get_db(db_session, test_db_engine):
    """Override database dependencies and AutoAPI engine for tests."""

    async def _get_test_db():
        yield db_session

    app.dependency_overrides[get_db] = _get_test_db

    original_provider = engine_resolver.resolve_provider(api=surface_api)
    spec = EngineSpec.from_any(TEST_DATABASE_URL)
    provider = Provider(spec)
    object.__setattr__(provider, "_engine", test_db_engine)
    maker = async_sessionmaker(
        test_db_engine, expire_on_commit=False, class_=AsyncSession
    )
    object.__setattr__(provider, "_maker", maker)
    engine_resolver.register_api(surface_api, provider)
    engine_resolver.resolve_provider(api=surface_api)
    try:
        yield
    finally:
        app.dependency_overrides.clear()
        engine_resolver.register_api(surface_api, original_provider)
        engine_resolver.resolve_provider(api=surface_api)


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
def enable_rfc7662():
    """Enable RFC 7662 token introspection for tests."""
    from tigrbl_auth.runtime_cfg import settings

    original = settings.enable_rfc7662
    settings.enable_rfc7662 = True
    try:
        yield
    finally:
        settings.enable_rfc7662 = original


@pytest.fixture
def enable_rfc7009():
    """Enable RFC 7009 token revocation for tests."""
    from tigrbl_auth.runtime_cfg import settings
    from tigrbl_auth.rfc7009 import include_rfc7009, reset_revocations

    original = settings.enable_rfc7009
    settings.enable_rfc7009 = True
    include_rfc7009(app)
    reset_revocations()
    try:
        yield
    finally:
        settings.enable_rfc7009 = original
        reset_revocations()


@pytest.fixture
def enable_rfc8693():
    """Enable RFC 8693 token exchange for tests."""
    from tigrbl_auth.runtime_cfg import settings
    from tigrbl_auth.rfc8693 import include_rfc8693

    original = settings.enable_rfc8693
    settings.enable_rfc8693 = True
    include_rfc8693(app)
    try:
        yield
    finally:
        settings.enable_rfc8693 = original


@pytest.fixture
def enable_rfc8414():
    """Enable RFC 8414 authorization server metadata for tests."""
    from tigrbl_auth.runtime_cfg import settings
    from tigrbl_auth.rfc8414 import include_rfc8414
    from tigrbl_auth.oidc_discovery import include_oidc_discovery

    original = settings.enable_rfc8414
    settings.enable_rfc8414 = True
    include_rfc8414(app)
    include_oidc_discovery(app)
    try:
        yield
    finally:
        settings.enable_rfc8414 = original


@pytest.fixture
def enable_rfc9126(db_session):
    """Enable RFC 9126 pushed authorization requests for tests."""
    from tigrbl_auth.runtime_cfg import settings
    from tigrbl_auth.rfc9126 import reset_par_store

    original = settings.enable_rfc9126
    settings.enable_rfc9126 = True
    asyncio.get_event_loop().run_until_complete(reset_par_store(db_session))
    try:
        yield
    finally:
        settings.enable_rfc9126 = original
        asyncio.get_event_loop().run_until_complete(reset_par_store(db_session))


@pytest.fixture
def temp_key_file():
    """Create a temporary key directory for testing."""
    temp_dir = Path(tempfile.mkdtemp())
    temp_kid = temp_dir / "jwt_ed25519.kid"

    import tigrbl_auth.crypto as crypto_module
    import tigrbl_auth.oidc_id_token as oidc_module

    original_dir = crypto_module._DEFAULT_KEY_DIR
    original_path = crypto_module._DEFAULT_KEY_PATH
    original_rsa_path = oidc_module._RSA_KEY_PATH

    crypto_module._DEFAULT_KEY_DIR = temp_dir
    crypto_module._DEFAULT_KEY_PATH = temp_kid
    crypto_module._provider.cache_clear()
    crypto_module._load_keypair.cache_clear()

    oidc_module._RSA_KEY_PATH = temp_dir / "jwt_rs256.kid"
    oidc_module._provider.cache_clear()
    oidc_module._service_cache = None

    yield temp_kid

    if temp_dir.exists():
        shutil.rmtree(temp_dir, ignore_errors=True)
    crypto_module._DEFAULT_KEY_DIR = original_dir
    crypto_module._DEFAULT_KEY_PATH = original_path
    crypto_module._provider.cache_clear()
    crypto_module._load_keypair.cache_clear()
    oidc_module._RSA_KEY_PATH = original_rsa_path
    oidc_module._provider.cache_clear()
    oidc_module._service_cache = None


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
