from pydantic import BaseModel

from tigrbl import alias_ctx, alias, schema_ctx
from tigrbl.op import resolve
from tigrbl.bindings import build_schemas, build_handlers


def _get_spec(model, target):
    specs = resolve(model)
    return next(sp for sp in specs if sp.target == target)


def test_alias_ctx_aliases_canonical_verb_and_preserves_core():
    @alias_ctx(create="register")
    class Thing:
        pass

    spec = _get_spec(Thing, "create")
    assert spec.alias == "register"

    # Build handlers to expose the alias and capture core step
    build_handlers(Thing, [spec])
    handler_step = Thing.handlers.register.HANDLER[0]
    assert handler_step.__name__ == "create"


def test_alias_ctx_request_schema_override():
    @alias_ctx(create=alias("register", request_schema="Reg.in"))
    class Thing:
        @schema_ctx(alias="Reg", kind="in")
        class RegIn(BaseModel):
            id: int

    spec = _get_spec(Thing, "create")
    build_schemas(Thing, [spec])
    assert Thing.schemas.register.in_ is Thing.RegIn


def test_alias_ctx_response_schema_override():
    @alias_ctx(create=alias("register", response_schema="Reg.out"))
    class Thing:
        @schema_ctx(alias="Reg", kind="out")
        class RegOut(BaseModel):
            id: int

    spec = _get_spec(Thing, "create")
    build_schemas(Thing, [spec])
    assert Thing.schemas.register.out is Thing.RegOut


def test_alias_ctx_persist_override():
    @alias_ctx(create=alias("register", persist="skip"))
    class Thing:
        pass

    spec = _get_spec(Thing, "create")
    assert spec.persist == "skip"


def test_alias_ctx_arity_override():
    @alias_ctx(create=alias("register", arity="member"))
    class Thing:
        pass

    spec = _get_spec(Thing, "create")
    assert spec.arity == "member"


def test_alias_ctx_rest_override():
    @alias_ctx(create=alias("register", rest=False))
    class Thing:
        pass

    spec = _get_spec(Thing, "create")
    assert spec.expose_routes is False
