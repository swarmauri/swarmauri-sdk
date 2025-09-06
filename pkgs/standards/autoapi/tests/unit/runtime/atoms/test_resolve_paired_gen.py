from types import SimpleNamespace

from autoapi.v3.column.io_spec import Pair
from autoapi.v3.runtime.atoms.resolve import paired_gen
from autoapi.v3.specs import IO


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


class ColIO:
    io = IO().paired(lambda ctx: Pair(raw="r", stored="s"), alias="extra")


def test_generate_paired_value_from_io() -> None:
    ctx = SimpleNamespace(persist=True, specs={"secret": ColIO()}, temp={})
    paired_gen.run(None, ctx)
    pv = ctx.temp["paired_values"]
    assert pv["secret"]["raw"] == "r"
