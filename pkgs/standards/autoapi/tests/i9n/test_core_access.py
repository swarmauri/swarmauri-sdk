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
from autoapi.v2 import AutoAPI, Base
from autoapi.v2.mixins import GUIDPk
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


class TestApiCore:
    """Test cases for api.core direct access (manual session management)."""

    def test_sync_core_create_success(self, sync_api):
        """Test successful creation using api.core with sync database."""
        api, get_db = sync_api
        user_data = {"name": "John Doe", "email": "john@example.com", "age": 30}

        with next(get_db()) as db:
            with db.begin():
                user = api.core.TestUsersCreate(user_data, db)
                db.flush()

                assert user.name == "John Doe"
                assert user.email == "john@example.com"
                assert user.age == 30
                assert user.id is not None

    def test_sync_core_read_success(self, sync_api):
        """Test successful read using api.core with sync database."""
        api, get_db = sync_api
        user_data = {"name": "Jane Doe", "email": "jane@example.com"}

        # First create a user
        with next(get_db()) as db:
            with db.begin():
                user = api.core.TestUsersCreate(user_data, db)
                db.flush()
                user_id = user.id

        # Then read it back
        with next(get_db()) as db:
            retrieved_user = api.core.TestUsersRead(user_id, db)
            assert retrieved_user.name == "Jane Doe"
            assert retrieved_user.email == "jane@example.com"
            assert retrieved_user.id == user_id

    def test_sync_core_update_success(self, sync_api):
        """Test successful update using api.core with sync database."""
        api, get_db = sync_api
        user_data = {"name": "Bob Smith", "email": "bob@example.com"}

        # Create user
        with next(get_db()) as db:
            with db.begin():
                user = api.core.TestUsersCreate(user_data, db)
                db.flush()
                user_id = user.id

        # Update user
        update_data = {"name": "Robert Smith", "age": 25}
        with next(get_db()) as db:
            with db.begin():
                updated_user = api.core.TestUsersUpdate(user_id, update_data, db)
                db.flush()

                assert updated_user.name == "Robert Smith"
                assert updated_user.email == "bob@example.com"  # Unchanged
                assert updated_user.age == 25

    def test_sync_core_delete_success(self, sync_api):
        """Test successful deletion using api.core with sync database."""
        api, get_db = sync_api
        user_data = {"name": "Delete Me", "email": "delete@example.com"}

        # Create user
        with next(get_db()) as db:
            with db.begin():
                user = api.core.TestUsersCreate(user_data, db)
                db.flush()
                user_id = user.id

        # Delete user
        with next(get_db()) as db:
            with db.begin():
                result = api.core.TestUsersDelete(user_id, db)
                db.flush()

                assert result == {"id": user_id}

    def test_sync_core_list_success(self, sync_api):
        """Test successful listing using api.core with sync database."""
        api, get_db = sync_api

        # Create multiple users
        users_data = [
            {"name": "User 1", "email": "user1@example.com"},
            {"name": "User 2", "email": "user2@example.com"},
            {"name": "User 3", "email": "user3@example.com"},
        ]

        with next(get_db()) as db:
            with db.begin():
                for user_data in users_data:
                    api.core.TestUsersCreate(user_data, db)
                db.flush()

        # List users
        with next(get_db()) as db:
            list_params = {"skip": 0, "limit": 10}
            users = api.core.TestUsersList(list_params, db)

            assert len(users) == 3
            assert all(user.name.startswith("User") for user in users)

    def test_sync_core_clear_success(self, sync_api):
        """Test successful clear using api.core with sync database."""
        api, get_db = sync_api

        # Create users
        with next(get_db()) as db:
            with db.begin():
                api.core.TestUsersCreate(
                    {"name": "User 1", "email": "user1@example.com"}, db
                )
                api.core.TestUsersCreate(
                    {"name": "User 2", "email": "user2@example.com"}, db
                )
                db.flush()

        # Clear all users
        with next(get_db()) as db:
            with db.begin():
                result = api.core.TestUsersClear(db)
                db.flush()

                assert result["deleted"] == 2

        # Verify empty
        with next(get_db()) as db:
            users = api.core.TestUsersList({}, db)
            assert len(users) == 0

    def test_sync_core_read_not_found(self, sync_api):
        """Test reading non-existent record raises HTTPException."""
        api, get_db = sync_api
        fake_id = "00000000-0000-0000-0000-000000000000"

        with pytest.raises(HTTPException) as exc_info:
            with next(get_db()) as db:
                api.core.TestUsersRead(fake_id, db)

        assert exc_info.value.status_code == 404

    def test_sync_core_update_not_found(self, sync_api):
        """Test updating non-existent record raises HTTPException."""
        api, get_db = sync_api
        fake_id = "00000000-0000-0000-0000-000000000000"
        update_data = {"name": "Updated"}

        with pytest.raises(HTTPException) as exc_info:
            with next(get_db()) as db:
                with db.begin():
                    api.core.TestUsersUpdate(fake_id, update_data, db)

        assert exc_info.value.status_code == 404

    def test_sync_core_delete_not_found(self, sync_api):
        """Test deleting non-existent record raises HTTPException."""
        api, get_db = sync_api
        fake_id = "00000000-0000-0000-0000-000000000000"

        with pytest.raises(HTTPException) as exc_info:
            with next(get_db()) as db:
                with db.begin():
                    api.core.TestUsersDelete(fake_id, db)

        assert exc_info.value.status_code == 404

    def test_sync_core_create_duplicate_email(self, sync_api):
        """Test creating user with duplicate email raises HTTPException."""
        api, get_db = sync_api
        user_data = {"name": "First User", "email": "duplicate@example.com"}

        # Create first user
        with next(get_db()) as db:
            with db.begin():
                api.core.TestUsersCreate(user_data, db)
                db.flush()

        # Try to create duplicate
        duplicate_data = {"name": "Second User", "email": "duplicate@example.com"}
        with pytest.raises(HTTPException) as exc_info:
            with next(get_db()) as db:
                with db.begin():
                    api.core.TestUsersCreate(duplicate_data, db)
                    db.flush()

        # SQLite returns 422 for constraint violations, PostgreSQL returns 409
        assert exc_info.value.status_code in (409, 422)

    def test_sync_core_manual_transaction_rollback(self, sync_api):
        """Test manual transaction rollback with api.core."""
        api, get_db = sync_api
        user_data = {"name": "Rollback User", "email": "rollback@example.com"}

        with next(get_db()) as db:
            with db.begin():
                user = api.core.TestUsersCreate(user_data, db)
                db.flush()
                user_id = user.id

                # Manually rollback
                db.rollback()

        # Verify user was not persisted
        with pytest.raises(HTTPException):
            with next(get_db()) as db:
                api.core.TestUsersRead(user_id, db)

    @pytest.mark.asyncio
    async def test_async_db_with_core_via_run_sync(self, async_api):
        """Test using api.core with async database via run_sync."""
        api, get_async_db = async_api
        user_data = {"name": "Async User", "email": "async@example.com"}

        async for db in get_async_db():
            # Use run_sync to call sync CRUD function
            result = await db.run_sync(
                lambda sync_db: api.core.TestUsersCreate(user_data, sync_db)
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
        user = await api.core_raw.TestUsersCreate(user_data)

        assert user.name == "Auto Session"
        assert user.email == "auto@example.com"
        assert user.id is not None

    @pytest.mark.asyncio
    async def test_sync_core_raw_create_manual_session(self, sync_api):
        """Test api.core_raw with manual session (sync)."""
        api, get_db = sync_api
        user_data = {"name": "Manual Session", "email": "manual@example.com"}

        with next(get_db()) as db:
            user = await api.core_raw.TestUsersCreate(user_data, db=db)
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
            user = await api.core_raw.TestUsersCreate(user_data, db=db)
            db.commit()  # Ensure it's persisted
            user_id = user.id

        # Read user back
        retrieved_user = await api.core_raw.TestUsersRead({"id": user_id})

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
            user = await api.core_raw.TestUsersCreate(user_data, db=db)
            db.commit()  # Ensure it's persisted
            user_id = user.id

        # Update user with manual session
        with next(get_db()) as db:
            update_data = {"id": user_id, "name": "Updated Name", "age": 35}
            updated_user = await api.core_raw.TestUsersUpdate(update_data, db=db)
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
            user = await api.core_raw.TestUsersCreate(user_data, db=db)
            db.commit()  # Ensure it's persisted
            user_id = user.id

        # Delete user with manual session
        with next(get_db()) as db:
            result = await api.core_raw.TestUsersDelete({"id": user_id}, db=db)
            db.commit()  # Ensure deletion is persisted

        assert result == {"id": user_id}

    @pytest.mark.asyncio
    async def test_sync_core_raw_list_success(self, sync_api):
        """Test successful listing using api.core_raw."""
        api, get_db = sync_api

        # Create multiple users with manual session to ensure they're committed
        with next(get_db()) as db:
            await api.core_raw.TestUsersCreate(
                {"name": "List User 1", "email": "list1@example.com"}, db=db
            )
            await api.core_raw.TestUsersCreate(
                {"name": "List User 2", "email": "list2@example.com"}, db=db
            )
            db.commit()  # Ensure they're persisted

        # List users
        list_params = {"skip": 0, "limit": 10}
        users = await api.core_raw.TestUsersList(list_params)

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
            await api.core_raw.TestUsersCreate(
                {"name": "Clear User 1", "email": "clear1@example.com"}, db=db
            )
            await api.core_raw.TestUsersCreate(
                {"name": "Clear User 2", "email": "clear2@example.com"}, db=db
            )
            db.commit()  # Ensure they're persisted

        # Clear all users with manual session
        with next(get_db()) as db:
            result = await api.core_raw.TestUsersClear({}, db=db)
            db.commit()  # Ensure clear is persisted

        assert result["deleted"] >= 2

        # Verify empty
        users = await api.core_raw.TestUsersList({})
        assert len(users) == 0

    @pytest.mark.asyncio
    async def test_async_core_raw_create_auto_session(self, async_api):
        """Test api.core_raw with async database and manual session (auto-session doesn't work with async-only setup)."""
        api, get_async_db = async_api
        user_data = {"name": "Async Auto", "email": "asyncauto@example.com"}

        # Since async-only API doesn't have sync get_db, we need to provide a manual session
        async for db in get_async_db():
            user = await api.core_raw.TestUsersCreate(user_data, db=db)
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
            user = await api.core_raw.TestUsersCreate(user_data, db=db)
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
        with pytest.raises(TypeError, match="core_exec requires a DB"):
            await api.core_raw.TestUsersCreate(user_data)

    @pytest.mark.asyncio
    async def test_core_raw_read_not_found(self, sync_api):
        """Test api.core_raw reading non-existent record."""
        api, get_db = sync_api
        fake_id = "00000000-0000-0000-0000-000000000000"

        with pytest.raises(HTTPException) as exc_info:
            await api.core_raw.TestUsersRead({"id": fake_id})

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_core_raw_update_not_found(self, sync_api):
        """Test api.core_raw updating non-existent record."""
        api, get_db = sync_api
        fake_id = "00000000-0000-0000-0000-000000000000"
        update_data = {"id": fake_id, "name": "Updated"}

        with pytest.raises(HTTPException) as exc_info:
            await api.core_raw.TestUsersUpdate(update_data)

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_core_raw_delete_not_found(self, sync_api):
        """Test api.core_raw deleting non-existent record."""
        api, get_db = sync_api
        fake_id = "00000000-0000-0000-0000-000000000000"

        with pytest.raises(HTTPException) as exc_info:
            await api.core_raw.TestUsersDelete({"id": fake_id})

        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_core_raw_create_duplicate_email(self, sync_api):
        """Test api.core_raw creating user with duplicate email."""
        api, get_db = sync_api

        # Create first user with manual session to ensure it's committed
        with next(get_db()) as db:
            await api.core_raw.TestUsersCreate(
                {"name": "First", "email": "dup@example.com"}, db=db
            )
            db.commit()  # Ensure it's persisted

        # Try to create duplicate with manual session to trigger constraint
        with pytest.raises(HTTPException) as exc_info:
            with next(get_db()) as db:
                await api.core_raw.TestUsersCreate(
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

        # Check that core exists and has expected methods
        assert hasattr(api, "core")
        assert hasattr(api.core, "TestUsersCreate")
        assert hasattr(api.core, "TestUsersRead")
        assert hasattr(api.core, "TestUsersUpdate")
        assert hasattr(api.core, "TestUsersDelete")
        assert hasattr(api.core, "TestUsersList")
        assert hasattr(api.core, "TestUsersClear")

        # Check that core_raw exists and has expected methods
        assert hasattr(api, "core_raw")
        assert hasattr(api.core_raw, "TestUsersCreate")
        assert hasattr(api.core_raw, "TestUsersRead")
        assert hasattr(api.core_raw, "TestUsersUpdate")
        assert hasattr(api.core_raw, "TestUsersDelete")
        assert hasattr(api.core_raw, "TestUsersList")
        assert hasattr(api.core_raw, "TestUsersClear")

    @pytest.mark.asyncio
    async def test_core_vs_core_raw_consistency(self, sync_api):
        """Test that core and core_raw produce consistent results."""
        api, get_db = sync_api

        # Create user with api.core
        user_data = {"name": "Consistency Test", "email": "consistency@example.com"}

        with next(get_db()) as db:
            with db.begin():
                core_user = api.core.TestUsersCreate(user_data, db)
                db.flush()
                core_user_id = core_user.id

        # Create user with api.core_raw using manual session to ensure it's committed
        user_data2 = {"name": "Consistency Test 2", "email": "consistency2@example.com"}
        with next(get_db()) as db:
            raw_user = await api.core_raw.TestUsersCreate(user_data2, db=db)
            db.commit()  # Ensure it's persisted
            raw_user_id = raw_user.id

        # Both should have similar structure
        assert core_user.name == user_data["name"]
        assert raw_user.name == user_data2["name"]
        assert core_user.email == user_data["email"]
        assert raw_user.email == user_data2["email"]

        # Read back with both methods
        with next(get_db()) as db:
            core_read = api.core.TestUsersRead(core_user_id, db)

        raw_read = await api.core_raw.TestUsersRead({"id": raw_user_id})

        # Results should be structurally similar
        assert core_read.id == core_user_id
        assert raw_read.id == raw_user_id
        assert core_read.name == user_data["name"]
        assert raw_read.name == user_data2["name"]
