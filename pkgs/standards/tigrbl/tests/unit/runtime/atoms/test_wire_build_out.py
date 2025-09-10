from types import SimpleNamespace

from tigrbl.runtime.atoms.wire import build_out
from tigrbl.runtime.kernel import (
    SchemaIn,
    SchemaOut,
    OpView,
    _default_kernel as K,
)


def test_build_out_reads_and_produces() -> None:
    class App:
        pass

    app = App()

    class Model:
        pass

    alias = "read"
    ov = OpView(
        schema_in=SchemaIn(fields=(), by_field={}),
        schema_out=SchemaOut(
            fields=("id", "virtual"),
            by_field={"id": {}, "virtual": {"virtual": True}},
            expose=("id", "virtual"),
        ),
        paired_index={},
        virtual_producers={"virtual": lambda obj, ctx: "v"},
        to_stored_transforms={},
        refresh_hints=(),
    )
    K._opviews[app] = {(Model, alias): ov}
    K._primed[app] = True

    ctx = SimpleNamespace(app=app, model=Model, op=alias, temp={})
    obj = SimpleNamespace(id=1)
    build_out.run(obj, ctx)
    assert ctx.temp["out_values"] == {"id": 1, "virtual": "v"}
