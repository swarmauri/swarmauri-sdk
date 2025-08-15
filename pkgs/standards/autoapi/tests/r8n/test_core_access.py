"""
Test cases for api.core and api.core_raw direct access methods.

Tests cover:
- Basic CRUD operations with api.core (manual session management)
- Basic CRUD operations with api.core_raw (automatic session management)
- Sync vs Async database compatibility
- Edge cases and error handling
- Session management edge cases
"""

import pytest
import pytest_asyncio
from autoapi.v3 import AutoAPI, Base
from autoapi.v3.mixins import GUIDPk
from sqlalchemy import Column, String, Integer
from fastapi import HTTPException


class CoreTestUser(Base, GUIDPk):
    __tablename__ = "test_users"
    name = Column(String(100), nullable=True)  # Allow partial updates
    email = Column(String(255), unique=True, nullable=True)  # Allow partial updates
    age = Column(Integer, nullable=True)


@pytest.fixture
def sync_api(sync_db_session):
    """Create sync AutoAPI instance with TestUser model."""
    engine, get_sync_db = sync_db_session
    Base.metadata.clear()

    api = AutoAPI(base=Base, include={CoreTestUser}, get_db=get_sync_db)
    api.initialize_sync()
    return api, get_sync_db


@pytest_asyncio.fixture
async def async_api(async_db_session):
    """Create async AutoAPI instance with TestUser model."""
    engine, get_async_db = async_db_session
    Base.metadata.clear()

    api = AutoAPI(base=Base, include={CoreTestUser}, get_async_db=get_async_db)
    await api.initialize_async()
    return api, get_async_db


def test_schemas_dir_contains_operation_names(sync_api):
    api, _ = sync_api
    names = dir(api.schemas)
    assert "CoreTestUserCreateIn" in names
    assert "CoreTestUser" not in names
    assert not hasattr(api.schemas, "CoreTestUser")


class TestApiCore:
    """Test cases for api.core direct access (manual session management)."""

    def test_sync_core_create_success(self, sync_api):
        """Test successful creation using api.core with schema validation."""
        api, get_db = sync_api

        # Use api.schemas for proper validation
        user_schema = api.schemas.CoreTestUserCreateIn(
            name="John Doe", email="john@example.com", age=30
        )

        with next(get_db()) as db:
            with db.begin():
                user = api.core.CoreTestUser.create(user_schema, db)
                db.flush()

                assert user.name == "John Doe"
                assert user.email == "john@example.com"
                assert user.age == 30
                assert user.id is not None

    def test_sync_core_read_success(self, sync_api):
        """Test successful read using api.core with schema validation."""
        api, get_db = sync_api

        # Use schema for creation
        user_schema = api.schemas.CoreTestUserCreateIn(
            name="Jane Doe", email="jane@example.com"
        )

        # First create a user
        with next(get_db()) as db:
            with db.begin():
                user = api.core.CoreTestUser.create(user_schema, db)
                db.flush()
                user_id = user.id

        # Then read it back - core.Read takes ID directly, not schema
        with next(get_db()) as db:
            retrieved_user = api.core.CoreTestUser.read(user_id, db)
            assert retrieved_user.name == "Jane Doe"
            assert retrieved_user.email == "jane@example.com"
            assert retrieved_user.id == user_id

    def test_sync_core_update_success(self, sync_api):
        """Test successful update using api.core with schema validation."""
        api, get_db = sync_api

        # Create user using schema
        user_schema = api.schemas.CoreTestUserCreateIn(
            name="Bob Smith", email="bob@example.com"
        )

        # Create user
        with next(get_db()) as db:
            with db.begin():
                user = api.core.CoreTestUser.create(user_schema, db)
                db.flush()
                user_id = user.id

        # Update user using schema for payload validation
        update_schema = api.schemas.CoreTestUserUpdateIn(name="Robert Smith", age=25)
        with next(get_db()) as db:
            with db.begin():
                updated_user = api.core.CoreTestUser.update(user_id, update_schema, db)
                db.flush()

                assert updated_user.name == "Robert Smith"
                assert updated_user.email == "bob@example.com"  # Unchanged
                assert updated_user.age == 25

    def test_sync_core_delete_success(self, sync_api):
        """Test successful deletion using api.core with schema validation."""
        api, get_db = sync_api

        # Create user using schema
        user_schema = api.schemas.CoreTestUserCreateIn(
            name="Delete Me", email="delete@example.com"
        )

        # Create user
        with next(get_db()) as db:
            with db.begin():
                user = api.core.CoreTestUser.create(user_schema, db)
                db.flush()
                user_id = user.id

        # Delete user - core.Delete takes ID directly
        with next(get_db()) as db:
            with db.begin():
                result = api.core.CoreTestUser.delete(user_id, db)
                db.flush()

                assert result == {"id": user_id}

    def test_sync_core_list_success(self, sync_api):
        """Test successful listing using api.core with schema validation."""
        api, get_db = sync_api

        # Create multiple users using schemas
        user_schemas = [
            api.schemas.CoreTestUserCreateIn(name="User 1", email="user1@example.com"),
            api.schemas.CoreTestUserCreateIn(name="User 2", email="user2@example.com"),
            api.schemas.CoreTestUserCreateIn(name="User 3", email="user3@example.com"),
        ]

        with next(get_db()) as db:
            with db.begin():
                for user_schema in user_schemas:
                    api.core.CoreTestUser.create(user_schema, db)
                db.flush()

        # List users using schema
        with next(get_db()) as db:
            list_schema = api.schemas.CoreTestUserListIn(skip=0, limit=10)
            users = api.core.CoreTestUser.list(list_schema, db)

            assert len(users) == 3
            assert all(user.name.startswith("User") for user in users)

    def test_sync_core_clear_success(self, sync_api):
        """Test successful clear using api.core with schema validation."""
        api, get_db = sync_api

        # Create users using schemas
        with next(get_db()) as db:
            with db.begin():
                user1_schema = api.schemas.CoreTestUserCreateIn(
                    name="User 1", email="user1@example.com"
                )
                user2_schema = api.schemas.CoreTestUserCreateIn(
                    name="User 2", email="user2@example.com"
                )
                api.core.CoreTestUser.create(user1_schema, db)
                api.core.CoreTestUser.create(user2_schema, db)
                db.flush()

        # Clear all users (clear only takes db parameter)
        with next(get_db()) as db:
            with db.begin():
                result = api.core.CoreTestUser.clear(db)
                db.flush()

                assert result["deleted"] == 2

        # Verify empty using schema
        with next(get_db()) as db:
            list_schema = api.schemas.CoreTestUserListIn()
            users = api.core.CoreTestUser.list(list_schema, db)
            assert len(users) == 0

    def test_sync_core_read_not_found(self, sync_api):
        """Test reading non-existent record raises HTTPException with schema validation."""
        api, get_db = sync_api
        fake_id = "00000000-0000-0000-0000-000000000000"

        with pytest.raises(HTTPException) as exc_info:
            with next(get_db()) as db:
                api.core.CoreTestUser.read(fake_id, db)

        assert exc_info.value.status_code == 404

    def test_sync_core_update_not_found(self, sync_api):
        """Test updating non-existent record raises HTTPException with schema validation."""
        api, get_db = sync_api
        fake_id = "00000000-0000-0000-0000-000000000000"

        update_schema = api.schemas.CoreTestUserUpdateIn(name="Updated")

        with pytest.raises(HTTPException) as exc_info:
            with next(get_db()) as db:
                with db.begin():
                    api.core.CoreTestUser.update(fake_id, update_schema, db)

        assert exc_info.value.status_code == 404

    def test_sync_core_delete_not_found(self, sync_api):
        """Test deleting non-existent record raises HTTPException with schema validation."""
        api, get_db = sync_api
        fake_id = "00000000-0000-0000-0000-000000000000"

        with pytest.raises(HTTPException) as exc_info:
            with next(get_db()) as db:
                with db.begin():
                    api.core.CoreTestUser.delete(fake_id, db)

        assert exc_info.value.status_code == 404

    def test_sync_core_create_duplicate_email(self, sync_api):
        """Test creating user with duplicate email raises HTTPException with schema validation."""
        api, get_db = sync_api

        first_user_schema = api.schemas.CoreTestUserCreateIn(
            name="First User", email="duplicate@example.com"
        )

        # Create first user
        with next(get_db()) as db:
            with db.begin():
                api.core.CoreTestUser.create(first_user_schema, db)
                db.flush()

        # Try to create duplicate using schema
        duplicate_schema = api.schemas.CoreTestUserCreateIn(
            name="Second User", email="duplicate@example.com"
        )
        with pytest.raises(HTTPException) as exc_info:
            with next(get_db()) as db:
                with db.begin():
                    api.core.CoreTestUser.create(duplicate_schema, db)
                    db.flush()

        # SQLite returns 422 for constraint violations, PostgreSQL returns 409
        assert exc_info.value.status_code in (409, 422)

    def test_sync_core_manual_transaction_rollback(self, sync_api):
        """Test manual transaction rollback with api.core and schema validation."""
        api, get_db = sync_api

        user_schema = api.schemas.CoreTestUserCreateIn(
            name="Rollback User", email="rollback@example.com"
        )

        with next(get_db()) as db:
            with db.begin():
                user = api.core.CoreTestUser.create(user_schema, db)
                db.flush()
                user_id = user.id

                # Manually rollback
                db.rollback()

        # Verify user was not persisted
        with pytest.raises(HTTPException):
            with next(get_db()) as db:
                api.core.CoreTestUser.read(user_id, db)

    @pytest.mark.asyncio
    async def test_async_db_with_core_via_run_sync(self, async_api):
        """Test using api.core with async database via run_sync and schema validation."""
        api, get_async_db = async_api

        user_schema = api.schemas.CoreTestUserCreateIn(
            name="Async User", email="async@example.com"
        )

        async for db in get_async_db():
            # Use run_sync to call sync CRUD function with schema
            result = await db.run_sync(
                lambda sync_db: api.core.CoreTestUser.create(user_schema, sync_db)
            )
            await db.commit()

            assert result.name == "Async User"
            assert result.email == "async@example.com"
            break


class TestApiCoreRaw:
    """Test cases for api.core_raw (automatic session management)."""

    @pytest.mark.asyncio
    async def test_sync_core_raw_create_auto_session(self, sync_api):
        """Test api.core_raw with automatic session management (sync)."""
        api, get_db = sync_api
        user_data = {"name": "Auto Session", "email": "auto@example.com"}

        # No manual session management required
        user = await api.core_raw.CoreTestUser.create(user_data)

        assert user.name == "Auto Session"
        assert user.email == "auto@example.com"
        assert user.id is not None

    @pytest.mark.asyncio
    async def test_sync_core_raw_create_manual_session(self, sync_api):
        """Test api.core_raw with manual session (sync)."""
        api, get_db = sync_api
        user_data = {"name": "Manual Session", "email": "manual@example.com"}

        with next(get_db()) as db:
            user = await api.core_raw.CoreTestUser.create(user_data, db=db)
            db.commit()  # Manual commit required

            assert user.name == "Manual Session"
            assert user.email == "manual@example.com"

    @pytest.mark.asyncio
    async def test_sync_core_raw_read_success(self, sync_api):
        """Test successful read using api.core_raw."""
        api, get_db = sync_api
        user_data = {"name": "Read Me", "email": "read@example.com"}

        # Create user with manual session to ensure it's committed
        with next(get_db()) as db:
            user = await api.core_raw.CoreTestUser.create(user_data, db=db)
            db.commit()  # Ensure it's persisted
            user_id = user.id

        # Read user back
        retrieved_user = await api.core_raw.CoreTestUser.read({"id": user_id})

        assert retrieved_user.name == "Read Me"
        assert retrieved_user.email == "read@example.com"
        assert retrieved_user.id == user_id

    @pytest.mark.asyncio
    async def test_sync_core_raw_update_success(self, sync_api):
        """Test successful update using api.core_raw."""
        api, get_db = sync_api
        user_data = {"name": "Update Me", "email": "update@example.com"}

        # Create user with manual session to ensure it's committed
        with next(get_db()) as db:
            user = await api.core_raw.CoreTestUser.create(user_data, db=db)
            db.commit()  # Ensure it's persisted
            user_id = user.id

        # Update user with manual session
        with next(get_db()) as db:
            update_data = {"id": user_id, "name": "Updated Name", "age": 35}
            updated_user = await api.core_raw.CoreTestUser.update(update_data, db=db)
            db.commit()  # Ensure update is persisted

        assert updated_user.name == "Updated Name"
        assert updated_user.email == "update@example.com"  # Unchanged
        assert updated_user.age == 35

    @pytest.mark.asyncio
    async def test_sync_core_raw_delete_success(self, sync_api):
        """Test successful deletion using api.core_raw."""
        api, get_db = sync_api
        user_data = {"name": "Delete Me Raw", "email": "deleteraw@example.com"}

        # Create user with manual session to ensure it's committed
        with next(get_db()) as db:
            user = await api.core_raw.CoreTestUser.create(user_data, db=db)
            db.commit()  # Ensure it's persisted
            user_id = user.id

        # Delete user with manual session
        with next(get_db()) as db:
            result = await api.core_raw.CoreTestUser.delete({"id": user_id}, db=db)
            db.commit()  # Ensure deletion is persisted

        assert result == {"id": user_id}

    @pytest.mark.asyncio
    async def test_sync_core_raw_list_success(self, sync_api):
        """Test successful listing using api.core_raw."""
        api, get_db = sync_api

        # Create multiple users with manual session to ensure they're committed
        with next(get_db()) as db:
            await api.core_raw.CoreTestUser.create(
                {"name": "List User 1", "email": "list1@example.com"}, db=db
            )
            await api.core_raw.CoreTestUser.create(
                {"name": "List User 2", "email": "list2@example.com"}, db=db
            )
            db.commit()  # Ensure they're persisted

        # List users
        list_params = {"skip": 0, "limit": 10}
        users = await api.core_raw.CoreTestUser.list(list_params)

        assert len(users) >= 2
        user_names = [u.name for u in users]
        assert "List User 1" in user_names
        assert "List User 2" in user_names

    @pytest.mark.asyncio
    async def test_sync_core_raw_clear_success(self, sync_api):
        """Test successful clear using api.core_raw."""
        api, get_db = sync_api

        # Create users first with manual session to ensure they're committed
        with next(get_db()) as db:
            await api.core_raw.CoreTestUser.create(
                {"name": "Clear User 1", "email": "clear1@example.com"}, db=db
            )
            await api.core_raw.CoreTestUser.create(
                {"name": "Clear User 2", "email": "clear2@example.com"}, db=db
            )
            db.commit()  # Ensure they're persisted

        # Clear all users with manual session
        with next(get_db()) as db:
            result = await api.core_raw.CoreTestUser.clear({}, db=db)
            db.commit()  # Ensure clear is persisted

        assert result["deleted"] >= 2

        # Verify empty
        users = await api.core_raw.CoreTestUser.list({})
        assert len(users) == 0

    @pytest.mark.asyncio
    async def test_async_core_raw_create_auto_session(self, async_api):
        """Test api.core_raw with async database and manual session (auto-session doesn't work with async-only setup)."""
        api, get_async_db = async_api
        user_data = {"name": "Async Auto", "email": "asyncauto@example.com"}

        # Since async-only API doesn't have sync get_db, we need to provide a manual session
        async for db in get_async_db():
            user = await api.core_raw.CoreTestUser.create(user_data, db=db)
            await db.commit()  # Ensure it's persisted

            assert user.name == "Async Auto"
            assert user.email == "asyncauto@example.com"
            assert user.id is not None
            break

    @pytest.mark.asyncio
    async def test_async_core_raw_create_manual_session(self, async_api):
        """Test api.core_raw with async database and manual session."""
        api, get_async_db = async_api
        user_data = {"name": "Async Manual", "email": "asyncmanual@example.com"}

        async for db in get_async_db():
            user = await api.core_raw.CoreTestUser.create(user_data, db=db)
            await db.commit()

            assert user.name == "Async Manual"
            assert user.email == "asyncmanual@example.com"
            break


class TestCoreRawEdgeCases:
    """Test edge cases and error conditions for api.core_raw."""

    @pytest.mark.asyncio
    async def test_core_raw_no_get_db_configured(self, async_db_session):
        """Test api.core_raw when no get_db is configured."""
        engine, get_async_db = async_db_session
        Base.metadata.clear()

        # Create API with only async_db, no sync get_db
        api = AutoAPI(base=Base, include={CoreTestUser}, get_async_db=get_async_db)
        await api.initialize_async()

        user_data = {"name": "No GetDB", "email": "nogetdb@example.com"}

        # Should raise TypeError when trying to auto-acquire session
        with pytest.raises(TypeError, match="core_raw requires a DB"):
            await api.core_raw.CoreTestUser.create(user_data)

    @pytest.mark.asyncio
    async def test_core_raw_read_not_found(self, sync_api):
        """Test api.core_raw reading non-existent record."""
        api, get_db = sync_api
        fake_id = "00000000-0000-0000-0000-000000000000"

        with pytest.raises(HTTPException) as exc_info:
            await api.core_raw.CoreTestUser.read({"id": fake_id})

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_core_raw_update_not_found(self, sync_api):
        """Test api.core_raw updating non-existent record."""
        api, get_db = sync_api
        fake_id = "00000000-0000-0000-0000-000000000000"
        update_data = {"id": fake_id, "name": "Updated"}

        with pytest.raises(HTTPException) as exc_info:
            await api.core_raw.CoreTestUser.update(update_data)

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_core_raw_delete_not_found(self, sync_api):
        """Test api.core_raw deleting non-existent record."""
        api, get_db = sync_api
        fake_id = "00000000-0000-0000-0000-000000000000"

        with pytest.raises(HTTPException) as exc_info:
            await api.core_raw.CoreTestUser.delete({"id": fake_id})

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_core_raw_create_duplicate_email(self, sync_api):
        """Test api.core_raw creating user with duplicate email."""
        api, get_db = sync_api

        # Create first user with manual session to ensure it's committed
        with next(get_db()) as db:
            await api.core_raw.CoreTestUser.create(
                {"name": "First", "email": "dup@example.com"}, db=db
            )
            db.commit()  # Ensure it's persisted

        # Try to create duplicate with manual session to trigger constraint
        with pytest.raises(HTTPException) as exc_info:
            with next(get_db()) as db:
                await api.core_raw.CoreTestUser.create(
                    {"name": "Second", "email": "dup@example.com"}, db=db
                )
                db.commit()  # This should trigger the constraint violation

        # SQLite returns 422 for constraint violations, PostgreSQL returns 409
        assert exc_info.value.status_code in (409, 422)


class TestCoreVsCoreRawComparison:
    """Compare behavior between api.core and api.core_raw."""

    def test_core_attributes_exist(self, sync_api):
        """Test that both core and core_raw attributes exist and have expected methods."""
        api, get_db = sync_api

        # Check that core exists and exposes resource operations
        assert hasattr(api, "core")
        assert hasattr(api.core, "CoreTestUser")
        assert hasattr(api.core.CoreTestUser, "create")
        assert hasattr(api.core.CoreTestUser, "read")
        assert hasattr(api.core.CoreTestUser, "update")
        assert hasattr(api.core.CoreTestUser, "delete")
        assert hasattr(api.core.CoreTestUser, "list")
        assert hasattr(api.core.CoreTestUser, "clear")

        # Check that core_raw exists and exposes resource operations
        assert hasattr(api, "core_raw")
        assert hasattr(api.core_raw, "CoreTestUser")
        assert hasattr(api.core_raw.CoreTestUser, "create")
        assert hasattr(api.core_raw.CoreTestUser, "read")
        assert hasattr(api.core_raw.CoreTestUser, "update")
        assert hasattr(api.core_raw.CoreTestUser, "delete")
        assert hasattr(api.core_raw.CoreTestUser, "list")
        assert hasattr(api.core_raw.CoreTestUser, "clear")

    @pytest.mark.asyncio
    async def test_core_vs_core_raw_consistency(self, sync_api):
        """Test that core and core_raw produce consistent results."""
        api, get_db = sync_api

        # Create user with api.core using schema validation
        user_schema = api.schemas.CoreTestUserCreateIn(
            name="Consistency Test", email="consistency@example.com"
        )

        with next(get_db()) as db:
            with db.begin():
                core_user = api.core.CoreTestUser.create(user_schema, db)
                db.flush()
                core_user_id = core_user.id

        # Create user with api.core_raw using raw dict (no schema validation)
        user_data2 = {"name": "Consistency Test 2", "email": "consistency2@example.com"}
        with next(get_db()) as db:
            raw_user = await api.core_raw.CoreTestUser.create(user_data2, db=db)
            db.commit()  # Ensure it's persisted
            raw_user_id = raw_user.id

        # Both should have similar structure
        assert core_user.name == "Consistency Test"
        assert raw_user.name == "Consistency Test 2"
        assert core_user.email == "consistency@example.com"
        assert raw_user.email == "consistency2@example.com"

        # Read back with both methods - core takes ID directly, core_raw uses dict
        with next(get_db()) as db:
            core_read = api.core.CoreTestUser.read(core_user_id, db)

        raw_read = await api.core_raw.CoreTestUser.read({"id": raw_user_id})

        # Results should be structurally similar
        assert core_read.id == core_user_id
        assert raw_read.id == raw_user_id
        assert core_read.name == "Consistency Test"
        assert raw_read.name == "Consistency Test 2"
