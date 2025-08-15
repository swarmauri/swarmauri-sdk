import pytest
from autoapi.v3 import get_schema


@pytest.mark.r8n
@pytest.mark.asyncio
async def test_schema_generation(api_client):
    client, _, Item = api_client

    create_model = get_schema(Item, "create")
    read_model = get_schema(Item, "read")
    update_model = get_schema(Item, "update")
    delete_model = get_schema(Item, "delete")
    list_model = get_schema(Item, "list")

    assert create_model.__name__ == "ItemCreate"
    assert read_model.__name__ == "ItemRead"
    assert update_model.__name__ == "ItemUpdate"
    assert delete_model.__name__ == "ItemDelete"
    assert list_model.__name__ == "ItemListParams"

    spec = (await client.get("/openapi.json")).json()
    schemas = spec["components"]["schemas"]
    assert create_model.__name__ in schemas


@pytest.mark.r8n
@pytest.mark.asyncio
async def test_bulk_operation_schema(api_client):
    client, _, _ = api_client
    spec = (await client.get("/openapi.json")).json()
    assert "/item/bulk" in spec["paths"]
    ops = spec["paths"]["/item/bulk"]
    assert "post" in ops and "delete" in ops
