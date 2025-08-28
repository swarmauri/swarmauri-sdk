import pytest
from autoapi.v3.types import App
from httpx import ASGITransport, AsyncClient
from sqlalchemy import Column, String

from autoapi.v3 import AutoAPI, op_ctx
from autoapi.v3.tables import Base
from autoapi.v3.mixins import GUIDPk
from autoapi.v3.core import crud


def setup_api(model_cls, get_db):
    Base.metadata.clear()
    app = App()
    api = AutoAPI(app=app, get_db=get_db)
    api.include_model(model_cls, prefix="")
    api.initialize_sync()
    return app, api


async def fetch_inspection(client):
    openapi = (await client.get("/openapi.json")).json()
    hookz = (await client.get("/hookz")).json()
    planz = (await client.get("/planz")).json()
    return openapi, hookz, planz


@pytest.mark.i9n
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "verb,alias,http_method,arity,needs_id,expected_status",
    [
        ("create", "make", "post", None, False, 201),
        ("read", "fetch", "get", "member", True, 404),
        ("update", "change", "put", "member", True, 404),
        ("delete", "remove", "delete", "member", True, 404),
        ("list", "browse", "get", "collection", False, 400),
        ("clear", "purge", "delete", "collection", False, 400),
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
    expected_status,
):
    _, get_sync_db = sync_db_session
    calls: list[str] = []
    orig = getattr(crud, verb)

    async def wrapped(*args, **kwargs):
        calls.append("core")
        return await orig(*args, **kwargs)

    monkeypatch.setattr(crud, verb, wrapped)

    class Widget(Base, GUIDPk):
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

    app, _ = setup_api(Widget, get_sync_db)

    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        wid = None
        if needs_id or verb in {"update", "delete", "list", "clear"}:
            r = await client.post("/widget", json={"name": "a"})
            wid = r.json()["id"]
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
        elif http_method == "put":
            res = await client.put(path, json=body)
        else:
            res = await client.delete(path)
        assert res.status_code == expected_status

        gen = get_sync_db()
        session = next(gen)
        count = session.query(Widget).count()
        obj = session.query(Widget).first()
        if verb == "create":
            assert count == 1
        elif verb == "update":
            assert obj.name == "a"
        elif verb == "delete":
            assert count == 1
        elif verb == "clear":
            assert count == 1
        else:
            assert count == 1
        try:
            next(gen)
        except StopIteration:
            pass

        openapi, _, _ = await fetch_inspection(client)
        assert path not in openapi["paths"]

    assert calls == []


@pytest.mark.i9n
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "verb,http_method,arity,needs_id",
    [
        ("create", "post", None, False),
        ("read", "get", "member", True),
        ("update", "put", "member", True),
        ("delete", "delete", "member", True),
        ("list", "get", "collection", False),
        ("clear", "delete", "collection", False),
    ],
)
async def test_op_ctx_override(sync_db_session, verb, http_method, arity, needs_id):
    _, get_sync_db = sync_db_session

    class Widget(Base, GUIDPk):
        __tablename__ = "widgets"
        __resource__ = "widget"
        name = Column(String)

        @op_ctx(target=verb, arity=arity)
        def _(cls, ctx):  # pragma: no cover - handler not invoked
            ctx["result"] = {"custom": True}
            return ctx["result"]

    app, _ = setup_api(Widget, get_sync_db)

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
            assert obj.name == "b"
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
