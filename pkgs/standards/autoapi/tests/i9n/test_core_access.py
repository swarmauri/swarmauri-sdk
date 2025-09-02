import pytest
import pytest_asyncio
from typing import Any, Mapping

from autoapi.v3.types import HTTPException, UUID, Column, Integer, String, uuid4

from autoapi.v3 import AutoApp, Base
from autoapi.v3.orm.mixins import GUIDPk, BulkCapable, Replaceable


class CoreTestUser(Base, GUIDPk, BulkCapable, Replaceable):
    __tablename__ = "test_users"
    name = Column(String(100), nullable=True)
    email = Column(String(255), unique=True, nullable=True)
    age = Column(Integer, nullable=True)


def _get(obj: Any, attr: str) -> Any:
    val = obj[attr] if isinstance(obj, Mapping) else getattr(obj, attr)
    return str(val) if isinstance(val, UUID) else val


@pytest.fixture
def sync_api(sync_db_session):
    """Create a sync AutoAPI instance with CoreTestUser."""
    _, get_sync_db = sync_db_session
    Base.metadata.clear()
    api = AutoApp(get_db=get_sync_db)
    api.include_model(CoreTestUser)
    api.initialize_sync()
    return api, get_sync_db


@pytest_asyncio.fixture
async def async_api(async_db_session):
    """Create an async AutoAPI instance with CoreTestUser."""
    _, get_db = async_db_session
    Base.metadata.clear()
    api = AutoApp(get_db=get_db)
    api.include_model(CoreTestUser)
    await api.initialize_async()
    return api, get_db


def test_api_exposes_core_proxies(sync_api):
    api, _ = sync_api
    assert hasattr(api.core, "CoreTestUser")
    assert hasattr(api.core_raw, "CoreTestUser")
    schema_ns = api.schemas.CoreTestUser
    for name in [
        "create",
        "read",
        "update",
        "delete",
        "list",
        "clear",
        "bulk_create",
        "bulk_update",
        "bulk_replace",
        "bulk_delete",
    ]:
        assert hasattr(schema_ns, name)


@pytest.mark.asyncio
async def test_core_and_core_raw_sync_operations(sync_api):
    api, get_db = sync_api
    with next(get_db()) as db:
        for proxy in (api.core, api.core_raw):
            model = proxy.CoreTestUser
            await model.clear({}, db=db)

            created = await model.create(
                {
                    "name": "John",
                    "email": f"john_{uuid4()}@example.com",
                    "age": 30,
                },
                db=db,
            )
            uid = _get(created, "id")
            assert uid is not None

            fetched = await model.read({"id": uid}, db=db)
            assert _get(fetched, "id") == uid

            updated = await model.update(
                {"age": 31}, db=db, ctx={"path_params": {"id": uid}}
            )
            assert updated is not None

            replaced = await model.replace(
                {"name": "Jane", "email": f"jane_{uid}@example.com"},
                db=db,
                ctx={"path_params": {"id": uid}},
            )
            assert replaced is not None

            listed = await model.list({}, db=db)
            assert any(_get(u, "id") == uid for u in listed)

            bulk_rows = [
                {
                    "name": "B1",
                    "email": f"b1_{uuid4()}@example.com",
                    "age": 20,
                },
                {
                    "name": "B2",
                    "email": f"b2_{uuid4()}@example.com",
                    "age": 21,
                },
            ]
            bulk_created = await model.bulk_create(bulk_rows, db=db)
            ids = [_get(u, "id") for u in bulk_created]
            bulk_updated = await model.bulk_update(
                [
                    {"id": ids[0], "age": 22},
                    {"id": ids[1], "age": 23},
                ],
                db=db,
            )
            assert all(_get(u, "age") in {22, 23} for u in bulk_updated)
            bulk_replaced = await model.bulk_replace(
                [
                    {
                        "id": ids[0],
                        "name": "R1",
                        "email": f"r1_{uuid4()}@example.com",
                        "age": 24,
                    },
                    {
                        "id": ids[1],
                        "name": "R2",
                        "email": f"r2_{uuid4()}@example.com",
                        "age": 25,
                    },
                ],
                db=db,
            )
            assert {_get(u, "name") for u in bulk_replaced} == {"R1", "R2"}
            deleted = await model.bulk_delete(ids, db=db)
            assert deleted["deleted"] == 2

            await model.clear({}, db=db)
            assert not await model.list({}, db=db)


@pytest.mark.asyncio
async def test_core_read_not_found(sync_api):
    api, get_db = sync_api
    fake_id = "00000000-0000-0000-0000-000000000000"
    with next(get_db()) as db:
        with pytest.raises(HTTPException):
            await api.core.CoreTestUser.read({"id": fake_id}, db=db)


@pytest.mark.asyncio
async def test_async_core_and_core_raw_create(async_api):
    api, get_db = async_api
    async for db in get_db():
        for proxy in (api.core, api.core_raw):
            user = await proxy.CoreTestUser.create(
                {
                    "id": str(uuid4()),
                    "name": "A",
                    "email": f"a_{uuid4()}@example.com",
                },
                db=db,
            )
            assert _get(user, "id") is not None
        break
