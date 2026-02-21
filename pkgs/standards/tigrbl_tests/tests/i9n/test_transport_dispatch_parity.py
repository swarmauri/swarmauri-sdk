from types import SimpleNamespace
import json

import pytest
import pytest_asyncio
from sqlalchemy import Column, String

from tigrbl import Base, TigrblApp, hook_ctx
from tigrbl.engine import resolver as _resolver
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.runtime.kernel import _default_kernel
from tigrbl.runtime.kernel.payload import build_kernelz_payload
from tigrbl.runtime.status import _RPC_TO_HTTP
from tigrbl.runtime.status.exceptions import HTTPException
from tigrbl.bindings.rpc import _serialize_output as _rpc_serialize_output
from tigrbl.transport.dispatch import dispatch_operation
from tigrbl.transport.jsonrpc.dispatcher import _dispatch_one


class _Req:
    def __init__(self, path: str, headers: dict[str, str] | None = None, app=None):
        self.url = f"http://test{path}"
        self.headers = headers or {}
        self.app = app
        self.state = SimpleNamespace()


@pytest_asyncio.fixture
async def parity_env():
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
    await app.initialize()

    db, release = _resolver.acquire(api=app, model=Widget, op_alias="create")
    try:
        yield app, Widget, db, trace
    finally:
        release()


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_transport_dispatch_parity_success_trace_and_kernelz(parity_env):
    app, Widget, db, trace = parity_env

    rest_result = await dispatch_operation(
        router=app,
        request=_Req("/widget", {"authorization": "Bearer ok"}, app),
        db=db,
        model_or_name=Widget,
        alias="create",
        payload={"name": "rest"},
        response_serializer=lambda r: _rpc_serialize_output(
            Widget, "create", "create", r
        ),
    )

    rpc_result = await _dispatch_one(
        api=app,
        request=_Req("/rpc", {"authorization": "Bearer ok"}, app),
        db=db,
        obj={
            "jsonrpc": "2.0",
            "id": "create-widget",
            "method": "Widget.create",
            "params": {"name": "rpc"},
        },
    )

    if hasattr(rest_result, "body"):
        rest_payload = json.loads(rest_result.body)
    else:
        rest_payload = rest_result
    assert set(rest_payload.keys()) == set(rpc_result["result"].keys())
    assert set(rpc_result.keys()) == {"jsonrpc", "result", "id"}

    kernelz = build_kernelz_payload(_default_kernel, app)
    assert "Widget" in kernelz
    assert "create" in kernelz["Widget"]
    assert any(step.startswith("PRE_TX") for step in kernelz["Widget"]["create"])

    assert trace["rest"] == ["PRE_TX_BEGIN", "POST_COMMIT"]
    assert trace["rpc"] == ["PRE_TX_BEGIN", "POST_COMMIT"]


@pytest.mark.i9n
@pytest.mark.asyncio
async def test_transport_dispatch_parity_secdep_failures(parity_env):
    app, Widget, db, trace = parity_env

    with pytest.raises(HTTPException) as rest_exc:
        await dispatch_operation(
            router=app,
            request=_Req("/widget", app=app),
            db=db,
            model_or_name=Widget,
            alias="create",
            payload={"name": "rest"},
        )

    rpc_response = await _dispatch_one(
        api=app,
        request=_Req("/rpc", app=app),
        db=db,
        obj={
            "jsonrpc": "2.0",
            "id": "create-widget-fail",
            "method": "Widget.create",
            "params": {"name": "rpc"},
        },
    )

    assert rest_exc.value.status_code == 401
    assert set(rpc_response.keys()) == {"jsonrpc", "error", "id"}
    assert set(rpc_response["error"].keys()) >= {"code", "message"}
    assert _RPC_TO_HTTP[rpc_response["error"]["code"]] == rest_exc.value.status_code
    assert trace["rest"] == ["PRE_TX_BEGIN"]
    assert trace["rpc"] == ["PRE_TX_BEGIN"]
