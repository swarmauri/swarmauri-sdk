"""Runtime behavior tests for column metadata keys."""

from datetime import datetime

import pytest
from autoapi.v3.types import App
from httpx import ASGITransport, AsyncClient

from autoapi.v3 import Base
from autoapi.v3.mixins import GUIDPk
from autoapi.v3.schema import _build_schema
from autoapi.v3.types import Column, DateTime, String, uuid4


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_write_only_field_runtime_behavior(create_test_api):
    """Ensure write_only fields are accepted but never returned."""

    class WriteOnlyModel(Base, GUIDPk):
        __tablename__ = "write_only_model"
        name = Column(String)
        secret = Column(String, info={"autoapi": {"write_only": True}})

    api = create_test_api(WriteOnlyModel)
    app = App()
    app.include_router(api.router)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        payload = {"id": str(uuid4()), "name": "test", "secret": "s3cr3t"}
        res = await client.post("/writeonlymodel", json=payload)
        assert res.status_code == 201
        item_id = res.json()["id"]

        res = await client.get(f"/writeonlymodel/{item_id}")
        assert res.status_code == 200
        assert "secret" not in res.json()

        res = await client.patch(
            f"/writeonlymodel/{item_id}", json={"secret": "newsecret"}
        )
        assert res.status_code == 200
        assert "secret" not in res.json()

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
    app = App()
    app.include_router(api.router)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        res = await client.post(
            "/readonlymodel", json={"id": str(uuid4()), "name": "bad", "code": "hack"}
        )
        assert res.status_code == 201
        data = res.json()
        item_id = data["id"]
        ro_value = data["code"]
        assert ro_value == "RO"

        res = await client.patch(f"/readonlymodel/{item_id}", json={"code": "hack"})
        assert res.status_code == 200
        assert res.json()["code"] == ro_value

        res = await client.patch(f"/readonlymodel/{item_id}", json={"name": "new"})
        assert res.status_code == 200
        assert res.json()["code"] == ro_value

        res = await client.get(f"/readonlymodel/{item_id}")
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
    """Ensure default_factory fields remain optional and refresh on updates."""

    class FactoryModel(Base, GUIDPk):
        __tablename__ = "factory_model"
        name = Column(String)
        created_at = Column(
            DateTime, info={"autoapi": {"default_factory": datetime.utcnow}}
        )

    api = create_test_api(FactoryModel)
    app = App()
    app.include_router(api.router)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        res = await client.post(
            "/factorymodel", json={"id": str(uuid4()), "name": "test"}
        )
        assert res.status_code == 201
        item_id = res.json()["id"]

        res = await client.get(f"/factorymodel/{item_id}")
        assert res.status_code == 200
        created_at = res.json()["created_at"]

        res = await client.patch(f"/factorymodel/{item_id}", json={"name": "updated"})
        assert res.status_code == 200

        res = await client.get(f"/factorymodel/{item_id}")
        assert res.status_code == 200
        assert res.json()["created_at"] != created_at

    create_schema = _build_schema(FactoryModel, verb="create")
    field = create_schema.model_fields["created_at"]
    assert field.default_factory is not None
    assert not field.is_required()
    assert "created_at" in _build_schema(FactoryModel, verb="read").model_fields
    assert "created_at" in _build_schema(FactoryModel, verb="update").model_fields
