import pytest
from autoapi.v3.schema import _build_schema
from autoapi.v3.types import BaseModel


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_schema_generation(api_client):
    client, _, Item = api_client

    create_model = _build_schema(Item, verb="create")
    read_model = _build_schema(Item, verb="read")
    update_model = _build_schema(Item, verb="update")
    delete_model = _build_schema(Item, verb="delete")
    list_model = _build_schema(Item, verb="list")

    assert issubclass(create_model, BaseModel)
    assert issubclass(read_model, BaseModel)
    assert issubclass(update_model, BaseModel)
    assert issubclass(delete_model, BaseModel)
    assert issubclass(list_model, BaseModel)

    assert create_model.__name__ == "ItemCreate"
    assert read_model.__name__ == "ItemRead"
    assert update_model.__name__ == "ItemUpdate"
    assert delete_model.__name__ == "ItemDelete"
    assert list_model.__name__ == "ItemList"

    spec = (await client.get("/openapi.json")).json()
    schemas = spec["components"]["schemas"]
    assert create_model.__name__ in schemas


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_bulk_operation_schema(api_client):
    client, _, _ = api_client
    spec = (await client.get("/openapi.json")).json()
    assert "/tenant/{tenant_id}" in spec["paths"]
    ops = spec["paths"]["/tenant/{tenant_id}"]
    assert "post" in ops and "delete" in ops
