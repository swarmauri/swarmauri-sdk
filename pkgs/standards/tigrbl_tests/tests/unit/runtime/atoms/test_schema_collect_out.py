from types import SimpleNamespace

from tigrbl.runtime.atoms.schema import collect_out
from tigrbl.runtime.kernel import (
    SchemaIn,
    SchemaOut,
    OpView,
    _default_kernel as K,
)


def test_collect_out_loads_schema() -> None:
    class App:
        pass

    app = App()

    class Model:
        pass

    alias = "read"
    schema_out = SchemaOut(
        fields=("name",),
        by_field={"name": {"alias_out": "alias", "sensitive": True}},
        expose=("name",),
    )
    ov = OpView(
        schema_in=SchemaIn(fields=(), by_field={}),
        schema_out=schema_out,
        paired_index={},
        virtual_producers={},
        to_stored_transforms={},
        refresh_hints=(),
    )
    K._opviews[app] = {(Model, alias): ov}
    K._primed[app] = True

    ctx = SimpleNamespace(app=app, model=Model, op=alias, temp={})
    collect_out.run(None, ctx)
    schema = ctx.temp["schema_out"]
    assert schema["by_field"]["name"]["sensitive"] is True
    assert schema["by_field"]["name"]["alias_out"] == "alias"
    assert "name" in schema["expose"]
