from types import SimpleNamespace

from tigrbl.runtime.atoms.resolve import assemble
from tigrbl.runtime.kernel import (
    SchemaIn,
    SchemaOut,
    OpView,
    _default_kernel as K,
)


def test_assemble_separates_virtual_and_persisted() -> None:
    class App:
        pass

    app = App()

    class Model:
        pass

    alias = "create"
    ov = OpView(
        schema_in=SchemaIn(
            fields=("name", "v"),
            by_field={"name": {"in_enabled": True}, "v": {"virtual": True}},
        ),
        schema_out=SchemaOut(fields=(), by_field={}, expose=()),
        paired_index={},
        virtual_producers={},
        to_stored_transforms={},
        refresh_hints=(),
    )
    K._opviews[app] = {(Model, alias): ov}
    K._primed[app] = True

    ctx = SimpleNamespace(
        app=app,
        model=Model,
        op=alias,
        persist=True,
        temp={"in_values": {"name": "Alice", "v": "x"}},
    )
    assemble.run(None, ctx)
    assert ctx.temp["assembled_values"] == {"name": "Alice"}
    assert ctx.temp["virtual_in"] == {"v": "x"}
