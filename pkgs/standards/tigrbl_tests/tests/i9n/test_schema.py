import pytest
from tigrbl.schema import _build_schema
from tigrbl.types import BaseModel


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_schema_generation(api_client):
    client, _, Item = api_client

    bulk_model = Item.schemas.bulk_create.in_item
    read_model = _build_schema(Item, verb="read")
    update_model = _build_schema(Item, verb="update")
    delete_model = _build_schema(Item, verb="delete")
    list_model = _build_schema(Item, verb="list")

    assert issubclass(bulk_model, BaseModel)
    assert issubclass(read_model, BaseModel)
    assert issubclass(update_model, BaseModel)
    assert issubclass(delete_model, BaseModel)
    assert issubclass(list_model, BaseModel)

    assert bulk_model.__name__.startswith("ItemBulkCreateItem")
    assert read_model.__name__ == "ItemRead"
    assert update_model.__name__ == "ItemUpdate"
    assert delete_model.__name__ == "ItemDelete"
    assert list_model.__name__ == "ItemList"

    spec = (await client.get("/openapi.json")).json()
    schemas = spec["components"]["schemas"]
    assert bulk_model.__name__ in schemas
    fields = getattr(bulk_model, "model_fields", None)
    if fields is None:
        fields = getattr(bulk_model, "__fields__", {})
    assert "tenant_id" not in fields


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_bulk_operation_schema(api_client):
    client, _, _ = api_client
    spec = (await client.get("/openapi.json")).json()
    assert "/tenant/{tenant_id}/item" in spec["paths"]
    ops = spec["paths"]["/tenant/{tenant_id}/item"]
    assert "post" in ops and "delete" in ops
