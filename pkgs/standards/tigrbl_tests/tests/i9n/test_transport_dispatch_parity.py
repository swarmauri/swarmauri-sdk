import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import Column, String

from tigrbl import Base, TigrblApp, hook_ctx
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.runtime.status import _RPC_TO_HTTP
from tigrbl.runtime.status.exceptions import HTTPException


@pytest_asyncio.fixture
async def parity_client():
    Base.metadata.clear()
    trace: dict[str, list[str]] = {"rest": [], "rpc": []}

    class Widget(Base, GUIDPk):
        __tablename__ = "widgets"
        name = Column(String, nullable=False)

        @hook_ctx(ops="create", phase="PRE_TX_BEGIN")
        async def trace_pre_tx(cls, ctx):
            bucket = "rpc" if "/rpc" in str(ctx["request"].url) else "rest"
            trace[bucket].append("PRE_TX_BEGIN")

        @hook_ctx(ops="create", phase="PRE_TX_BEGIN")
        async def require_auth_header(cls, ctx):
            if ctx["request"].headers.get("authorization") != "Bearer ok":
                raise HTTPException(status_code=401, detail="Unauthorized")

        @hook_ctx(ops="create", phase="POST_COMMIT")
        async def trace_post_commit(cls, ctx):
            bucket = "rpc" if "/rpc" in str(ctx["request"].url) else "rest"
            trace[bucket].append("POST_COMMIT")

    app = TigrblApp(engine=mem())
    app.include_model(Widget, prefix="")
    app.mount_jsonrpc(prefix="/rpc")
    app.attach_diagnostics(prefix="/system")
    await app.initialize()

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client, trace


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_transport_dispatch_parity_success_trace_and_kernelz(parity_client):
    client, trace = parity_client

    rest = await client.post(
        "/widget", json={"name": "rest"}, headers={"authorization": "Bearer ok"}
    )
    assert rest.status_code == 201

    rpc = await client.post(
        "/rpc",
        json={
            "jsonrpc": "2.0",
            "id": "create-widget",
            "method": "Widget.create",
            "params": {"name": "rpc"},
        },
        headers={"authorization": "Bearer ok"},
    )
    assert rpc.status_code == 200
    assert "result" in rpc.json()

    kernelz_resp = await client.get("/system/kernelz")
    if kernelz_resp.status_code == 404:
        kernelz_resp = await client.get("/kernelz")
    assert kernelz_resp.status_code == 200
    kernelz = kernelz_resp.json()
    assert "Widget" in kernelz
    assert "create" in kernelz["Widget"]
    assert trace["rest"] == ["PRE_TX_BEGIN", "POST_COMMIT"]
    assert trace["rpc"] == ["PRE_TX_BEGIN", "POST_COMMIT"]
    assert trace["rest"] == trace["rpc"]


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_transport_dispatch_parity_secdep_failures(parity_client):
    client, _ = parity_client

    rest = await client.post("/widget", json={"name": "rest"})
    rpc = await client.post(
        "/rpc",
        json={
            "jsonrpc": "2.0",
            "id": "create-widget-fail",
            "method": "Widget.create",
            "params": {"name": "rpc"},
        },
    )

    assert rest.status_code == 401
    rpc_body = rpc.json()
    assert rpc.status_code == 200
    assert set(rpc_body.keys()) == {"jsonrpc", "error", "id"}
    assert set(rpc_body["error"].keys()) >= {"code", "message"}
    assert _RPC_TO_HTTP[rpc_body["error"]["code"]] == rest.status_code
