from types import SimpleNamespace

from tigrbl.runtime.atoms.out import masking
from tigrbl.runtime.kernel import (
    SchemaIn,
    SchemaOut,
    OpView,
    _default_kernel as K,
)


def test_out_masking_applies_to_sensitive_fields() -> None:
    class App:
        pass

    app = App()

    class Model:
        pass

    alias = "read"
    ov = OpView(
        schema_in=SchemaIn(fields=(), by_field={}),
        schema_out=SchemaOut(
            fields=("secret", "public"),
            by_field={"secret": {"sensitive": True}, "public": {}},
            expose=("secret", "public"),
        ),
        paired_index={},
        virtual_producers={},
        to_stored_transforms={},
        refresh_hints=(),
    )
    K._opviews[app] = {(Model, alias): ov}
    K._primed[app] = True

    temp = {
        "response_payload": {"secret": "abcd1234", "token": "abc", "public": "x"},
        "emit_aliases": {"pre": [], "post": [{"alias": "token"}], "read": []},
    }
    ctx = SimpleNamespace(app=app, model=Model, op=alias, temp=temp)
    masking.run(None, ctx)
    assert ctx.temp["response_payload"]["secret"] == "••••1234"
    assert ctx.temp["response_payload"]["token"] == "abc"


def test_out_masking_handles_missing_payload_gracefully() -> None:
    class App:
        pass

    app = App()

    class Model:
        pass

    alias = "read"
    ov = OpView(
        schema_in=SchemaIn(fields=(), by_field={}),
        schema_out=SchemaOut(
            fields=("secret",),
            by_field={"secret": {"sensitive": True}},
            expose=("secret",),
        ),
        paired_index={},
        virtual_producers={},
        to_stored_transforms={},
        refresh_hints=(),
    )
    K._opviews[app] = {(Model, alias): ov}
    K._primed[app] = True

    temp = {}
    ctx = SimpleNamespace(app=app, model=Model, op=alias, temp=temp)
    masking.run(None, ctx)
    assert "response_payload" not in ctx.temp
    assert "emit_aliases" not in ctx.temp
