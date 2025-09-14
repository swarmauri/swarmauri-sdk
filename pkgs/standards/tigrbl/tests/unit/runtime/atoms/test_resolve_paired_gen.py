from types import SimpleNamespace

from tigrbl.runtime.atoms.resolve import paired_gen
from tigrbl.runtime.kernel import (
    SchemaIn,
    SchemaOut,
    OpView,
    _default_kernel as K,
)


def test_generate_paired_value() -> None:
    class App:
        pass

    app = App()

    class Model:
        pass

    alias = "create"
    ov = OpView(
        schema_in=SchemaIn(fields=("secret",), by_field={"secret": {}}),
        schema_out=SchemaOut(fields=(), by_field={}, expose=()),
        paired_index={"secret": {}},
        virtual_producers={},
        to_stored_transforms={},
        refresh_hints=(),
    )
    K._opviews[app] = {(Model, alias): ov}
    K._primed[app] = True

    ctx = SimpleNamespace(app=app, model=Model, op=alias, persist=True, temp={})
    paired_gen.run(None, ctx)
    pv = ctx.temp["paired_values"]
    pf = ctx.temp["persist_from_paired"]
    assert "secret" in pv and "raw" in pv["secret"]
    assert pf["secret"]["source"] == ("paired_values", "secret", "raw")


def test_generate_paired_value_from_io() -> None:
    class App:
        pass

    app = App()

    class Model:
        pass

    alias = "create"
    ov = OpView(
        schema_in=SchemaIn(fields=("secret",), by_field={"secret": {}}),
        schema_out=SchemaOut(fields=(), by_field={}, expose=()),
        paired_index={"secret": {"gen": lambda ctx: "r"}},
        virtual_producers={},
        to_stored_transforms={},
        refresh_hints=(),
    )
    K._opviews[app] = {(Model, alias): ov}
    K._primed[app] = True

    ctx = SimpleNamespace(app=app, model=Model, op=alias, persist=True, temp={})
    paired_gen.run(None, ctx)
    pv = ctx.temp["paired_values"]
    assert pv["secret"]["raw"] == "r"
