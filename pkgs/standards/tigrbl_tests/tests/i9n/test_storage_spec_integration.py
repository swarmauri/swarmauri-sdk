import pytest
from tigrbl.core import crud
from tigrbl.types import String


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_storage_spec_request_response_schema(router_client):
    client, router, Widget, _ = router_client
    create_schema = router.schemas.Widget.create.in_
    read_schema = router.schemas.Widget.read.out
    assert create_schema.model_fields["name"].is_required()
    assert not create_schema.model_fields["age"].is_required()
    assert "secret" in read_schema.model_fields


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_storage_spec_columns(router_client):
    _, _, Widget, _ = router_client
    table = Widget.__table__
    assert table.c.name.nullable is False
    assert table.c.age.default.arg == 5


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_storage_spec_default_resolution(router_client):
    client, _, _, _ = router_client
    resp = await client.post("/widget", json={"name": "A", "secret": "s"})
    assert resp.status_code == 201
    assert resp.json()["age"] == 5


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_storage_spec_internal_orm(router_client):
    _, router, Widget, _ = router_client
    assert router.models["Widget"] is Widget
    assert "age" in router.columns["Widget"]


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_storage_spec_openapi(router_client):
    client, _, _, _ = router_client
    spec = (await client.get("/openapi.json")).json()
    schema = spec["components"]["schemas"]["WidgetCreateRequest"]
    assert "name" in schema["required"]
    assert "age" not in schema["required"]


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_storage_spec_storage_sqlalchemy(router_client):
    client, _, Widget, session_maker = router_client
    resp = await client.post("/widget", json={"name": "B", "secret": "abc"})
    item_id = resp.json()["id"]
    async with session_maker() as session:
        await session.get(Widget, item_id)
        assert isinstance(Widget.__table__.c.name.type, String)


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_storage_spec_rest_calls(router_client):
    client, _, _, _ = router_client
    resp = await client.post("/widget", json={"name": "C", "secret": "xyz"})
    item_id = resp.json()["id"]
    read = await client.get(f"/widget/{item_id}")
    assert read.status_code == 200
    assert read.json()["id"] == item_id


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_storage_spec_rpc_methods(router_client):
    client, _, _, _ = router_client
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
async def test_storage_spec_core_crud(router_client):
    _, router, Widget, session_maker = router_client
    async with session_maker() as session:
        obj = await crud.create(Widget, {"name": "core", "secret": "def"}, db=session)
        await session.commit()
    assert obj.age == 5


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_storage_spec_hookz(router_client):
    client, _, _, _ = router_client
    hooks = (await client.get("/system/hookz")).json()
    assert "Widget" in hooks
    assert "create" in hooks["Widget"]


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_storage_spec_atomz(router_client):
    client, _, _, _ = router_client
    kernelz = (await client.get("/system/kernelz")).json()
    steps = kernelz["Widget"]["create"]
    assert "HANDLER:hook:wire:tigrbl:core:crud:ops:create@HANDLER" in steps


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_storage_spec_system_steps(router_client):
    client, _, _, _ = router_client
    kernelz = (await client.get("/system/kernelz")).json()
    assert "Widget" in kernelz
    assert "create" in kernelz["Widget"]
