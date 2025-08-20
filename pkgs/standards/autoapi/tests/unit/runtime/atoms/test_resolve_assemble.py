from types import SimpleNamespace

from autoapi.v3.runtime.atoms.resolve import assemble


class PersistCol:
    def __init__(self) -> None:
        self.storage = object()


class VirtualCol:
    storage = None


def test_assemble_separates_virtual_and_persisted() -> None:
    specs = {"name": PersistCol(), "v": VirtualCol()}
    ctx = SimpleNamespace(
        persist=True, specs=specs, temp={"in_values": {"name": "Alice", "v": "x"}}
    )
    assemble.run(None, ctx)
    assert ctx.temp["assembled_values"] == {"name": "Alice"}
    assert ctx.temp["virtual_in"] == {"v": "x"}
