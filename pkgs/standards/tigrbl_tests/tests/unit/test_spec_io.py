from tigrbl.column import F, IO
from tigrbl.column.io_spec import Pair


def test_io_spec_assemble_and_alias_readtime():
    spec = IO(in_verbs=("create",), out_verbs=("read",))
    derived = spec.assemble(
        ["first", "last"], lambda payload, ctx: " ".join(payload.values())
    )
    assert derived._assemble is not None
    assert derived._assemble.sources == ("first", "last")

    aliased = derived.alias_readtime("display", lambda obj, ctx: "ok")
    assert len(aliased._readtime_aliases) == 1
    alias = aliased._readtime_aliases[0]
    assert alias.name == "display"
    assert alias.alias_field.py_type is str


def test_io_spec_paired_behavior():
    def _make(ctx):
        return Pair(raw="raw", stored="stored")

    spec = IO().paired(
        _make, alias="token", verbs=("create",), alias_field=F(py_type=str)
    )
    assert spec._paired is not None
    assert spec._paired.alias == "token"
    assert spec._paired.verbs == ("create",)
