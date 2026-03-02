import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from tigrbl import TigrblApp
from tigrbl._spec import F, IO, S, acol
from tigrbl.orm.tables import TableBase
from tigrbl.shortcuts.engine import mem
from tigrbl.types import Integer, Mapped, String


@pytest_asyncio.fixture()
async def jsonrpc_client():
    TableBase.metadata.clear()
    TableBase.registry.dispose()

    class Tenant(TableBase):
        __tablename__ = "tenants"
        __allow_unmapped__ = True

        id: Mapped[int] = acol(
            storage=S(type_=Integer, primary_key=True, autoincrement=True)
        )
        name: Mapped[str] = acol(
            storage=S(type_=String, nullable=False),
            field=F(required_in=("create",)),
            io=IO(
                in_verbs=("create", "update", "replace"),
                out_verbs=("read", "list"),
            ),
        )

        __tigrbl_cols__ = {"id": id, "name": name}

    app = TigrblApp(engine=mem(async_=False))
    app.include_table(Tenant, prefix="")
    await app.initialize()
    transport = ASGITransport(app=app)
    client = AsyncClient(transport=transport, base_url="http://test")
    try:
        yield client
    finally:
        await client.aclose()


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_jsonrpc_batch_executes_in_order(jsonrpc_client):
    create_resp = await jsonrpc_client.post(
        "/rpc",
        json={
            "jsonrpc": "2.0",
            "method": "Tenant.create",
            "params": {"name": "batch-tenant"},
            "id": 1,
        },
    )
    list_resp = await jsonrpc_client.post(
        "/rpc",
        json={
            "jsonrpc": "2.0",
            "method": "Tenant.list",
            "params": {},
            "id": 2,
        },
    )

    assert create_resp.status_code == 200
    assert list_resp.status_code == 200
    assert create_resp.json()["id"] == 1
    assert list_resp.json()["id"] == 2
    assert create_resp.json()["result"]["name"] == "batch-tenant"
    assert "result" in list_resp.json()


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_jsonrpc_batch_reports_errors_per_item(jsonrpc_client):
    ok_resp = await jsonrpc_client.post(
        "/rpc",
        json={
            "jsonrpc": "2.0",
            "method": "Tenant.list",
            "params": {},
            "id": 10,
        },
    )
    err_resp = await jsonrpc_client.post(
        "/rpc",
        json={
            "jsonrpc": "2.0",
            "method": "Tenant",
            "params": {},
            "id": 11,
        },
    )

    assert ok_resp.status_code == 200
    assert err_resp.status_code == 404
    assert ok_resp.json()["id"] == 10
    assert "result" in ok_resp.json()
