from types import SimpleNamespace

from autoapi.v3.runtime.atoms.resolve import paired_gen


class Col:
    def __init__(self) -> None:
        self.paired = True


def test_generate_paired_value() -> None:
    ctx = SimpleNamespace(persist=True, specs={"secret": Col()}, temp={})
    paired_gen.run(None, ctx)
    pv = ctx.temp["paired_values"]
    pf = ctx.temp["persist_from_paired"]
    assert "secret" in pv and "raw" in pv["secret"]
    assert pf["secret"]["source"] == ("paired_values", "secret", "raw")
