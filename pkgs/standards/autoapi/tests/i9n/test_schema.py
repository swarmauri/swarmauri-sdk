import pytest
from autoapi.v2 import AutoAPI


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_schema_generation(api_client):
    client, _, Item = api_client

    create_model = AutoAPI.get_schema(Item, "create")
    read_model = AutoAPI.get_schema(Item, "read")
    update_model = AutoAPI.get_schema(Item, "update")
    delete_model = AutoAPI.get_schema(Item, "delete")
    list_model = AutoAPI.get_schema(Item, "list")

    assert create_model.__name__ == "ItemCreate"
    assert read_model.__name__ == "ItemRead"
    assert update_model.__name__ == "ItemUpdate"
    assert delete_model.__name__ == "ItemDelete"
    assert list_model.__name__ == "ItemsListParams"

    spec = (await client.get("/openapi.json")).json()
    schemas = spec["components"]["schemas"]
    assert create_model.__name__ in schemas


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_bulk_operation_schema(api_client):
    client, _, _ = api_client
    spec = (await client.get("/openapi.json")).json()
    assert "/items/bulk" in spec["paths"]
    ops = spec["paths"]["/items/bulk"]
    assert "post" in ops and "delete" in ops
