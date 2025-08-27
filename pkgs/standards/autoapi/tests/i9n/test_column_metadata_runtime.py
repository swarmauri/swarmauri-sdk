"""Runtime behavior tests for column metadata keys."""

from datetime import datetime
from uuid import UUID

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy import Column, DateTime, String

from autoapi.v3 import Base
from autoapi.v3.mixins import GUIDPk
from autoapi.v3.schema import _build_schema


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_write_only_field_runtime_behavior(create_test_api):
    """Ensure write_only fields are accepted but never returned."""

    class WriteOnlyModel(Base, GUIDPk):
        __tablename__ = "write_only_model"
        name = Column(String)
        secret = Column(String, info={"autoapi": {"write_only": True}})

    api = create_test_api(WriteOnlyModel)
    app = FastAPI()
    app.include_router(api.router)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        payload = {"name": "test", "secret": "s3cr3t"}
        res = await client.post("/write_only_model", json=payload)
        assert res.status_code == 201
        item_id = res.json()["id"]

        gen = api.get_db()
        session = next(gen)
        try:
            obj = session.get(WriteOnlyModel, UUID(item_id))
            assert obj.secret == "s3cr3t"
        finally:
            try:
                next(gen)
            except StopIteration:
                pass

        res = await client.get(f"/write_only_model/{item_id}")
        assert res.status_code == 200
        assert "secret" not in res.json()

        res = await client.patch(
            f"/write_only_model/{item_id}", json={"secret": "newsecret"}
        )
        assert res.status_code == 200
        assert "secret" not in res.json()

        gen = api.get_db()
        session = next(gen)
        try:
            obj = session.get(WriteOnlyModel, UUID(item_id))
            assert obj.secret == "newsecret"
        finally:
            try:
                next(gen)
            except StopIteration:
                pass

    create_schema = _build_schema(WriteOnlyModel, verb="create")
    read_schema = _build_schema(WriteOnlyModel, verb="read")
    update_schema = _build_schema(WriteOnlyModel, verb="update")

    assert "secret" in create_schema.model_fields
    assert "secret" in update_schema.model_fields
    assert "secret" not in read_schema.model_fields


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_read_only_field_runtime_behavior(create_test_api):
    """Ensure read_only fields are returned but cannot be written."""

    class ReadOnlyModel(Base, GUIDPk):
        __tablename__ = "read_only_model"
        name = Column(String)
        code = Column(String, default="RO", info={"autoapi": {"read_only": True}})

    api = create_test_api(ReadOnlyModel)
    app = FastAPI()
    app.include_router(api.router)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        res = await client.post(
            "/read_only_model", json={"name": "bad", "code": "hack"}
        )
        assert res.status_code == 201
        data = res.json()
        item_id = data["id"]
        ro_value = data["code"]
        assert ro_value == "RO"

        res = await client.patch(f"/read_only_model/{item_id}", json={"code": "hack"})
        assert res.status_code == 200
        assert res.json()["code"] == ro_value

        res = await client.patch(f"/read_only_model/{item_id}", json={"name": "new"})
        assert res.status_code == 200
        assert res.json()["code"] == ro_value

        res = await client.get(f"/read_only_model/{item_id}")
        assert res.status_code == 200
        assert res.json()["code"] == ro_value

    create_schema = _build_schema(ReadOnlyModel, verb="create")
    read_schema = _build_schema(ReadOnlyModel, verb="read")
    update_schema = _build_schema(ReadOnlyModel, verb="update")

    assert "code" not in create_schema.model_fields
    assert "code" in read_schema.model_fields
    assert "code" not in update_schema.model_fields


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_default_factory_field_runtime_behavior(create_test_api):
    """Ensure default_factory populates missing values and persists across updates."""

    class FactoryModel(Base, GUIDPk):
        __tablename__ = "factory_model"
        name = Column(String)
        created_at = Column(
            DateTime, info={"autoapi": {"default_factory": datetime.utcnow}}
        )

    api = create_test_api(FactoryModel)
    app = FastAPI()
    app.include_router(api.router)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        res = await client.post("/factory_model", json={"name": "test"})
        assert res.status_code == 201
        data = res.json()
        item_id = data["id"]
        created = data["created_at"]

        res = await client.get(f"/factory_model/{item_id}")
        assert res.status_code == 200
        assert res.json()["created_at"] == created

        res = await client.patch(f"/factory_model/{item_id}", json={"name": "updated"})
        assert res.status_code == 200
        assert res.json()["created_at"] == created

    create_schema = _build_schema(FactoryModel, verb="create")
    field = create_schema.model_fields["created_at"]
    assert field.default_factory is not None
    assert not field.is_required()
    assert "created_at" in _build_schema(FactoryModel, verb="read").model_fields
    assert "created_at" in _build_schema(FactoryModel, verb="update").model_fields
