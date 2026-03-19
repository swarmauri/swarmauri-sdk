import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import Column, String
from uuid import uuid4
from tigrbl import TigrblApp, TigrblRouter, op_ctx
from tigrbl import core as _core
from tigrbl.core import crud
from tigrbl.orm.mixins import GUIDPk
from tigrbl.orm.tables import TableBase


def setup_app(model_cls, get_db):
    TableBase.metadata.clear()
    app = TigrblApp()
    router = TigrblRouter(get_db=get_db)
    app.include_table(model_cls, prefix="")
    app.include_router(router)
    app.initialize()
    return app


async def fetch_inspection(client):
    openapi = (await client.get("/openapi.json")).json()
    hookz = (await client.get("/hookz")).json()
    kernelz = (await client.get("/kernelz")).json()
    return openapi, hookz, kernelz


@pytest.mark.i9n
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "verb,alias,http_method,arity,needs_id,seed_record,expected_status",
    [
        ("create", "make", "post", None, False, False, 201),
        ("read", "fetch", "get", "member", True, False, 404),
        ("update", "change", "patch", "member", True, False, 404),
        ("delete", "remove", "delete", "member", True, False, 404),
        ("list", "browse", "get", "collection", False, True, 200),
        ("clear", "purge", "delete", "collection", False, True, 200),
    ],
)
async def test_op_ctx_alias(
    monkeypatch,
    sync_db_session,
    verb,
    alias,
    http_method,
    arity,
    needs_id,
    seed_record,
    expected_status,
):
    _, get_sync_db = sync_db_session
    calls: list[str] = []
    orig = getattr(_core, verb)

    async def wrapped(*args, **kwargs):
        calls.append("core")
        return await orig(*args, **kwargs)

    # Patch both the re-exported core function and the underlying crud module
    monkeypatch.setattr(_core, verb, wrapped)
    monkeypatch.setattr(crud, verb, wrapped)

    class Widget(TableBase, GUIDPk):
        __tablename__ = "widgets"
        __resource__ = "widget"
        name = Column(String)

        @op_ctx(alias=alias, target=verb, arity=arity)
        def _(cls, ctx):  # pragma: no cover - handler not invoked
            calls.append("op")
            if verb == "update" and ctx.get("obj"):
                ctx["obj"].name = "b"
            if verb == "clear":
                ctx["result"] = {"cleared": True}
            return ctx.get("obj") or ctx.get("result")

    app = setup_app(Widget, get_sync_db)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        wid = None
        if seed_record:
            r = await client.post("/widget", json={"name": "a"})
            wid = r.json()["id"]
        elif needs_id:
            wid = str(uuid4())
        path = f"/widget/{wid}/{alias}" if needs_id else f"/widget/{alias}"
        body = (
            {"name": "b"}
            if verb == "update"
            else {"name": "a"}
            if verb == "create"
            else None
        )
        if http_method == "post":
            res = await client.post(path, json=body)
        elif http_method == "get":
            res = await client.get(path)
        elif http_method == "patch":
            res = await client.patch(path, json=body)
        elif http_method == "put":
            res = await client.put(path, json=body)
        else:
            res = await client.delete(path)
        assert res.status_code == expected_status

        gen = get_sync_db()
        session = next(gen)
        count = session.query(Widget).count()
        obj = session.query(Widget).first()
        if seed_record and verb not in {"clear"}:
            assert count == 1
        elif verb == "create":
            assert count == 1
        elif verb == "update":
            assert obj is None
        elif verb == "delete":
            assert count == 0
        elif verb == "clear":
            assert count == 0
        else:
            assert count == 0
        try:
            next(gen)
        except StopIteration:
            pass

        openapi, _, _ = await fetch_inspection(client)
        assert path in openapi["paths"]

    assert "op" in calls
    if verb in {"create", "read", "update", "delete", "list", "clear"}:
        assert "core" in calls


@pytest.mark.i9n
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "verb,http_method,arity,needs_id",
    [
        ("create", "post", None, False),
        ("read", "get", "member", True),
        ("update", "patch", "member", True),
        ("delete", "delete", "member", True),
        ("list", "get", "collection", False),
        ("clear", "delete", "collection", False),
    ],
)
async def test_op_ctx_override(sync_db_session, verb, http_method, arity, needs_id):
    _, get_sync_db = sync_db_session

    class Widget(TableBase, GUIDPk):
        __tablename__ = "widgets"
        __resource__ = "widget"
        name = Column(String)

        @op_ctx(target=verb, arity=arity)
        def _(cls, ctx):  # pragma: no cover - handler not invoked
            ctx["result"] = {"custom": True}
            return ctx["result"]

    app = setup_app(Widget, get_sync_db)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        wid = None
        if needs_id or verb in {"update", "delete", "list", "clear"}:
            r = await client.post("/widget", json={"name": "a"})
            wid = r.json()["id"]
        path = f"/widget/{wid}" if needs_id else "/widget"
        body = (
            {"name": "b"}
            if verb == "update"
            else {"name": "a"}
            if verb == "create"
            else None
        )
        if http_method == "post":
            res = await client.post(path, json=body)
        elif http_method == "get":
            res = await client.get(path)
        elif http_method == "patch":
            res = await client.patch(path, json=body)
        elif http_method == "put":
            res = await client.put(path, json=body)
        else:
            res = await client.delete(path)
        assert res.status_code in {200, 201}

        gen = get_sync_db()
        session = next(gen)
        count = session.query(Widget).count()
        if verb == "create":
            assert count == 1
        elif verb == "read":
            assert count == 1 if wid else 0
        elif verb == "update":
            obj = session.query(Widget).first()
            # Overriding the update target bypasses the core updater
            assert obj.name == "a"
        elif verb == "delete":
            assert count == 0
        elif verb == "list":
            assert count == 1
        elif verb == "clear":
            assert count == 0
        try:
            next(gen)
        except StopIteration:
            pass

        openapi, _, _ = await fetch_inspection(client)
        template = "/widget/{item_id}" if needs_id else "/widget"
        assert template in openapi["paths"]
