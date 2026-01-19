import pytest
import tigrbl.core as core
from pydantic import BaseModel

from tigrbl import alias_ctx, alias, schema_ctx
from tigrbl.op import resolve
from tigrbl.bindings import build_schemas, build_handlers


@pytest.mark.asyncio
async def test_alias_ctx_renames_canon_and_uses_core_handler(monkeypatch):
    called = {}

    async def fake_read(model, ident, db=None):
        called["args"] = (model, ident, db)
        return {"id": ident}

    monkeypatch.setattr(core, "read", fake_read)

    @alias_ctx(read="get")
    class Widget:
        pass

    specs = resolve(Widget)
    sp = next(sp for sp in specs if sp.alias == "get")
    assert sp.target == "read"

    build_handlers(Widget, specs)

    ctx = {"path_params": {"id": 7}}
    result = await Widget.handlers.get.raw(ctx)
    assert result == {"id": 7}
    assert called["args"] == (Widget, 7, None)
    assert Widget.handlers.get.raw.__name__ == fake_read.__name__


def test_alias_ctx_request_schema_override():
    @alias_ctx(create=alias("add", request_schema="Payload.in"))
    class Widget:
        @schema_ctx(alias="Payload", kind="in")
        class Payload(BaseModel):
            x: int

    specs = resolve(Widget)
    build_schemas(Widget, specs)
    assert Widget.schemas.add.in_ is Widget.Payload


def test_alias_ctx_response_schema_override():
    @alias_ctx(read=alias("fetch", response_schema="Result.out"))
    class Widget:
        @schema_ctx(alias="Result", kind="out")
        class Result(BaseModel):
            id: int

    specs = resolve(Widget)
    build_schemas(Widget, specs)
    assert Widget.schemas.fetch.out is Widget.Result


def test_alias_ctx_persist_override():
    @alias_ctx(update=alias("modify", persist="skip"))
    class Widget:
        pass

    specs = resolve(Widget)
    sp = next(sp for sp in specs if sp.alias == "modify")
    assert sp.persist == "skip"


def test_alias_ctx_arity_override():
    @alias_ctx(list=alias("ls", arity="member"))
    class Widget:
        pass

    specs = resolve(Widget)
    sp = next(sp for sp in specs if sp.alias == "ls")
    assert sp.arity == "member"


def test_alias_ctx_rest_override():
    @alias_ctx(delete=alias("remove", rest=False))
    class Widget:
        pass

    specs = resolve(Widget)
    sp = next(sp for sp in specs if sp.alias == "remove")
    assert sp.expose_routes is False
