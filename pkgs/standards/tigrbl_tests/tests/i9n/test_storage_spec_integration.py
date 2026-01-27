import pytest
from tigrbl.core import crud
from tigrbl.types import String


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_storage_spec_request_response_schema(api_client_v3):
    client, api, Widget, _ = api_client_v3
    create_schema = api.schemas.Widget.create.in_
    read_schema = api.schemas.Widget.read.out
    assert create_schema.model_fields["name"].is_required()
    assert not create_schema.model_fields["age"].is_required()
    assert "secret" in read_schema.model_fields


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_storage_spec_columns(api_client_v3):
    _, _, Widget, _ = api_client_v3
    table = Widget.__table__
    assert table.c.name.nullable is False
    assert table.c.age.default.arg == 5


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_storage_spec_default_resolution(api_client_v3):
    client, _, _, _ = api_client_v3
    resp = await client.post("/widget", json={"name": "A", "secret": "s"})
    assert resp.status_code == 201
    assert resp.json()["age"] == 5


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_storage_spec_internal_orm(api_client_v3):
    _, api, Widget, _ = api_client_v3
    assert api.models["Widget"] is Widget
    assert "age" in api.columns["Widget"]


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_storage_spec_openapi(api_client_v3):
    client, _, _, _ = api_client_v3
    spec = (await client.get("/openapi.json")).json()
    schema = spec["components"]["schemas"]["WidgetCreateRequest"]
    assert "name" in schema["required"]
    assert "age" not in schema["required"]


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_storage_spec_storage_sqlalchemy(api_client_v3):
    client, _, Widget, session_maker = api_client_v3
    resp = await client.post("/widget", json={"name": "B", "secret": "abc"})
    item_id = resp.json()["id"]
    async with session_maker() as session:
        await session.get(Widget, item_id)
        assert isinstance(Widget.__table__.c.name.type, String)


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_storage_spec_rest_calls(api_client_v3):
    client, _, _, _ = api_client_v3
    resp = await client.post("/widget", json={"name": "C", "secret": "xyz"})
    item_id = resp.json()["id"]
    read = await client.get(f"/widget/{item_id}")
    assert read.status_code == 200
    assert read.json()["id"] == item_id


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_storage_spec_rpc_methods(api_client_v3):
    client, _, _, _ = api_client_v3
    payload = {"name": "rpc", "secret": "mno"}
    resp = await client.post(
        "/rpc/",
        json={
            "jsonrpc": "2.0",
            "id": 1,
            "method": "Widget.create",
            "params": payload,
        },
    )
    assert resp.json()["result"]["name"] == "rpc"


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_storage_spec_core_crud(api_client_v3):
    _, api, Widget, session_maker = api_client_v3
    async with session_maker() as session:
        obj = await crud.create(Widget, {"name": "core", "secret": "def"}, db=session)
        await session.commit()
    assert obj.age == 5


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_storage_spec_hookz(api_client_v3):
    client, _, _, _ = api_client_v3
    hooks = (await client.get("/system/hookz")).json()
    assert "Widget" in hooks
    assert "create" in hooks["Widget"]


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_storage_spec_atomz(api_client_v3):
    client, _, _, _ = api_client_v3
    kernelz = (await client.get("/system/kernelz")).json()
    steps = kernelz["Widget"]["create"]
    assert "HANDLER:hook:wire:tigrbl:core:crud:ops:create@HANDLER" in steps


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_storage_spec_system_steps(api_client_v3):
    client, _, _, _ = api_client_v3
    kernelz = (await client.get("/system/kernelz")).json()
    assert "Widget" in kernelz
    assert "create" in kernelz["Widget"]
