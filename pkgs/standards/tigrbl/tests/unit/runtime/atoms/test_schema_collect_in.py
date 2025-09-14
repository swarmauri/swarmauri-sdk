from types import SimpleNamespace

from tigrbl.runtime.atoms.schema import collect_in
from tigrbl.runtime.kernel import (
    SchemaIn,
    SchemaOut,
    OpView,
    _default_kernel as K,
)


def test_collect_in_builds_schema() -> None:
    class App:
        pass

    app = App()

    class Model:
        pass

    alias = "create"
    ov = OpView(
        schema_in=SchemaIn(
            fields=("name", "v"),
            by_field={
                "name": {"alias_in": "alias", "required": True},
                "v": {"virtual": True},
            },
        ),
        schema_out=SchemaOut(fields=(), by_field={}, expose=()),
        paired_index={},
        virtual_producers={},
        to_stored_transforms={},
        refresh_hints=(),
    )
    K._opviews[app] = {(Model, alias): ov}
    K._primed[app] = True

    ctx = SimpleNamespace(app=app, model=Model, op=alias, temp={})
    collect_in.run(None, ctx)
    schema = ctx.temp["schema_in"]
    assert schema["by_field"]["name"]["alias_in"] == "alias"
    assert "name" in schema["required"]
    assert schema["by_field"]["v"]["virtual"] is True
