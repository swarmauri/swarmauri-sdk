import pytest
from autoapi.v3.schema import _build_schema


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_schema_generation(api_client):
    client, _, Item = api_client

    create_model = _build_schema(Item, verb="create")
    read_model = _build_schema(Item, verb="read")
    update_model = _build_schema(Item, verb="update")
    delete_model = _build_schema(Item, verb="delete")
    list_model = _build_schema(Item, verb="list")

    assert create_model.__name__ == "ItemCreate"
    assert read_model.__name__ == "ItemRead"
    assert update_model.__name__ == "ItemUpdate"
    assert delete_model.__name__ == "ItemDelete"
    assert list_model.__name__ == "ItemListParams"

    spec = (await client.get("/openapi.json")).json()
    schemas = spec["components"]["schemas"]
    assert create_model.__name__ in schemas


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_bulk_operation_schema(api_client):
    client, _, _ = api_client
    spec = (await client.get("/openapi.json")).json()
    assert "/item/bulk" in spec["paths"]
    ops = spec["paths"]["/item/bulk"]
    assert "post" in ops and "delete" in ops
