from types import SimpleNamespace

from tigrbl.runtime.atoms.emit import paired_pre
from tigrbl.runtime.kernel import (
    SchemaIn,
    SchemaOut,
    OpView,
    _default_kernel as K,
)


def test_paired_pre_records_descriptor() -> None:
    class App:
        pass

    app = App()

    class Model:
        pass

    alias = "create"
    ov = OpView(
        schema_in=SchemaIn(fields=(), by_field={}),
        schema_out=SchemaOut(fields=(), by_field={}, expose=()),
        paired_index={"token": {"alias": "t"}},
        virtual_producers={},
        to_stored_transforms={},
        refresh_hints=(),
    )
    K._opviews[app] = {(Model, alias): ov}
    K._primed[app] = True

    temp = {"paired_values": {"token": {"raw": "abc", "alias": "t"}}}
    ctx = SimpleNamespace(app=app, model=Model, op=alias, persist=True, temp=temp)
    paired_pre.run(None, ctx)
    pre = ctx.temp["emit_aliases"]["pre"]
    assert pre[0]["field"] == "token"
    assert pre[0]["alias"] == "t"
