from types import SimpleNamespace

from tigrbl.runtime.atoms.emit import readtime_alias
from tigrbl.runtime.kernel import (
    SchemaIn,
    SchemaOut,
    OpView,
    _default_kernel as K,
)


def test_readtime_alias_masks_sensitive_value() -> None:
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
            by_field={"secret": {"alias_out": "hint", "sensitive": True}},
            expose=("secret",),
        ),
        paired_index={},
        virtual_producers={},
        to_stored_transforms={},
        refresh_hints=(),
    )
    K._opviews[app] = {(Model, alias): ov}
    K._primed[app] = True

    temp = {"response_extras": {}, "emit_aliases": {"pre": [], "post": [], "read": []}}
    ctx = SimpleNamespace(app=app, model=Model, op=alias, temp=temp)
    obj = SimpleNamespace(secret="abcd1234")
    readtime_alias.run(obj, ctx)
    assert ctx.temp["response_extras"]["hint"] == "••••1234"
