from __future__ import annotations

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy import Column, String

from tigrbl import Base, TigrblApp
from tigrbl.engine.shortcuts import mem
from tigrbl.op import OpSpec
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import HTTPException


@pytest_asyncio.fixture
async def parity_client():
    Base.metadata.clear()
    trace: list[str] = []

    def secdep_ok(ctx):
        trace.append("secdep_ok")

    def dep_ok(ctx):
        trace.append("dep_ok")

    def secdep_fail(_ctx):
        raise HTTPException(status_code=403, detail="secdep blocked")

    class Widget(Base, GUIDPk):
        __tablename__ = "widgets_transport_parity"
        name = Column(String, nullable=False)
        __tigrbl_ops__ = [
            OpSpec(
                alias="create", target="create", secdeps=(secdep_ok,), deps=(dep_ok,)
            ),
            OpSpec(
                alias="deny",
                target="custom",
                arity="collection",
                secdeps=(secdep_fail,),
            ),
        ]

        @classmethod
        def deny(cls, ctx):
            return {"ok": True}

    app = TigrblApp()
    api = TigrblApp(engine=mem())
    api.include_model(Widget, prefix="")
    api.mount_jsonrpc(prefix="/rpc")
    await api.initialize()
    app.include_router(api.router)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client, trace


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_rest_and_rpc_dispatch_parity(parity_client):
    client, trace = parity_client

    kernelz_before = (await client.get("/kernelz")).json()

    trace.clear()
    rest_res = await client.post("/widget", json={"name": "rest"})
    rest_trace = list(trace)

    trace.clear()
    rpc_res = await client.post(
        "/rpc",
        json={
            "jsonrpc": "2.0",
            "method": "Widget.create",
            "params": {"name": "rpc"},
            "id": 1,
        },
    )
    rpc_trace = list(trace)

    kernelz_after = (await client.get("/kernelz")).json()

    assert rest_res.status_code == 201
    assert rpc_res.status_code == 200
    assert set(rest_res.json()) == set(rpc_res.json()["result"])
    assert rest_trace == rpc_trace == ["secdep_ok", "dep_ok"]
    assert kernelz_before == kernelz_after
    assert kernelz_before["Widget"]["create"] == kernelz_after["Widget"]["create"]


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_rest_and_rpc_secdep_error_parity(parity_client):
    client, _ = parity_client

    rest_res = await client.post("/widget/deny", json={})
    rpc_res = await client.post(
        "/rpc",
        json={
            "jsonrpc": "2.0",
            "method": "Widget.deny",
            "params": {},
            "id": 2,
        },
    )

    assert rest_res.status_code == 403
    assert rest_res.json()["detail"] == "secdep blocked"
    assert rpc_res.status_code == 200
    payload = rpc_res.json()
    assert payload["error"]["code"] == -32002
    assert payload["error"]["message"] == "secdep blocked"
