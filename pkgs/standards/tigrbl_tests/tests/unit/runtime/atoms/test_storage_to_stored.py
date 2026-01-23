from types import SimpleNamespace

from tigrbl.runtime.atoms.storage import to_stored
from tigrbl.runtime.kernel import (
    SchemaIn,
    SchemaOut,
    OpView,
    _default_kernel as K,
)


def test_to_stored_derives_from_paired_raw() -> None:
    class App:
        pass

    app = App()

    class Model:
        pass

    alias = "create"

    def deriver(raw: str, ctx: object) -> str:  # pragma: no cover - simple
        return raw.upper()

    ov = OpView(
        schema_in=SchemaIn(fields=("token",), by_field={"token": {}}),
        schema_out=SchemaOut(fields=(), by_field={}, expose=()),
        paired_index={"token": {"store": deriver}},
        virtual_producers={},
        to_stored_transforms={},
        refresh_hints=(),
    )
    K._opviews[app] = {(Model, alias): ov}
    K._primed[app] = True

    temp = {
        "paired_values": {"token": {"raw": "abc"}},
        "persist_from_paired": {"token": {"source": ("paired_values", "token", "raw")}},
        "assembled_values": {},
    }
    ctx = SimpleNamespace(app=app, model=Model, op=alias, persist=True, temp=temp)
    to_stored.run(None, ctx)
    assert ctx.temp["assembled_values"]["token"] == "ABC"
    assert ctx.temp["storage_log"][0]["action"] == "derived_from_paired"
