from types import SimpleNamespace

from tigrbl.runtime.atoms.refresh import demand
from tigrbl.runtime.kernel import (
    SchemaIn,
    SchemaOut,
    OpView,
    _default_kernel as K,
)


def test_refresh_demand_marks_need() -> None:
    class App:
        pass

    app = App()

    class Model:
        pass

    alias = "create"
    ov = OpView(
        schema_in=SchemaIn(fields=(), by_field={}),
        schema_out=SchemaOut(fields=(), by_field={}, expose=()),
        paired_index={},
        virtual_producers={},
        to_stored_transforms={},
        refresh_hints=("id",),
    )
    K._opviews[app] = {(Model, alias): ov}
    K._primed[app] = True

    ctx = SimpleNamespace(
        app=app,
        model=Model,
        op=alias,
        persist=True,
        temp={},
        cfg=SimpleNamespace(),
    )
    demand.run(None, ctx)
    assert ctx.temp["refresh_demand"] is True
    assert ctx.temp["refresh_fields"] == ("id",)
