from types import SimpleNamespace

from autoapi.v3.runtime.atoms.wire import build_out


class PersistCol:
    def __init__(self) -> None:
        self.storage = object()


class VirtualCol:
    storage = None

    def read_producer(
        self, obj: object, ctx: object
    ) -> str:  # pragma: no cover - simple
        return "v"


def test_build_out_reads_and_produces() -> None:
    specs = {"id": PersistCol(), "virtual": VirtualCol()}
    schema_out = {"by_field": {"id": {}, "virtual": {}}, "expose": ("id", "virtual")}
    ctx = SimpleNamespace(temp={"schema_out": schema_out}, specs=specs)
    obj = SimpleNamespace(id=1)
    build_out.run(obj, ctx)
    assert ctx.temp["out_values"] == {"id": 1, "virtual": "v"}
