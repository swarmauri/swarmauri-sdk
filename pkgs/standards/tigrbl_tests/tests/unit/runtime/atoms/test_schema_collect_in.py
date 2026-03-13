from types import SimpleNamespace

from tigrbl_atoms.atoms.schema.collect_in import _run as collect_in_run
from tigrbl_kernel import (
    SchemaIn,
    SchemaOut,
    OpView,
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
    ctx = SimpleNamespace(app=app, model=Model, op=alias, opview=ov, temp={})
    collect_in_run(None, ctx)
    schema = ctx.temp["schema_in"]
    assert schema["by_field"]["name"]["alias_in"] == "alias"
    assert "name" in schema["required"]
    assert schema["by_field"]["v"]["virtual"] is True
