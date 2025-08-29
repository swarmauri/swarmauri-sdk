import pytest
import pytest_asyncio
from typing import Any, Mapping

from autoapi.v3.types import HTTPException, UUID, Column, Integer, String, uuid4

from autoapi.v3 import AutoAPI, Base
from autoapi.v3.mixins import GUIDPk


class CoreTestUser(Base, GUIDPk):
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
    api = AutoAPI(get_db=get_sync_db)
    api.include_model(CoreTestUser)
    api.initialize_sync()
    return api, get_sync_db


@pytest_asyncio.fixture
async def async_api(async_db_session):
    """Create an async AutoAPI instance with CoreTestUser."""
    _, get_async_db = async_db_session
    Base.metadata.clear()
    api = AutoAPI(get_async_db=get_async_db)
    api.include_model(CoreTestUser)
    await api.initialize_async()
    return api, get_async_db


def test_api_exposes_core_proxies(sync_api):
    api, _ = sync_api
    assert hasattr(api.core, "CoreTestUser")
    assert hasattr(api.core_raw, "CoreTestUser")
    schema_ns = api.schemas.CoreTestUser
    for name in ["create", "read", "update", "delete", "list", "clear"]:
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

            await model.clear({}, db=db)
            assert not await model.list({}, db=db)

            rows = [
                {
                    "name": "A",
                    "email": f"a_{uid}@example.com",
                },
                {
                    "name": "B",
                    "email": f"b_{uid}@example.com",
                },
            ]
            created_rows = await model.bulk_create(rows, db=db)
            ids = [r["id"] if isinstance(r, Mapping) else r.id for r in created_rows]
            assert len(ids) == 2

            upd_rows = [
                {"id": ids[0], "age": 20},
                {"id": ids[1], "age": 21},
            ]
            updated_rows = await model.bulk_update(upd_rows, db=db)
            assert {_get(u, "age") for u in updated_rows} == {20, 21}

            rep_rows = [
                {"id": ids[0], "name": "A1", "email": f"a1_{uid}@example.com"},
                {"id": ids[1], "name": "B1", "email": f"b1_{uid}@example.com"},
            ]
            replaced_rows = await model.bulk_replace(rep_rows, db=db)
            assert {_get(r, "name") for r in replaced_rows} == {"A1", "B1"}

            del_payload = {"ids": ids}
            await model.bulk_delete(None, db=db, ctx={"payload": del_payload})
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
    api, get_async_db = async_api
    async for db in get_async_db():
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
