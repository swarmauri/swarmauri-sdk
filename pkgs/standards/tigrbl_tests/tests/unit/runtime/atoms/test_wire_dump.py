from types import SimpleNamespace

from tigrbl.runtime.atoms.wire import dump


def test_dump_applies_alias_and_omits_nulls() -> None:
    temp = {
        "out_values": {"a": None, "b": 1},
        "schema_out": {"aliases": {"b": "B"}},
        "response_extras": {"extra": 2},
    }
    ctx = SimpleNamespace(temp=temp, cfg=SimpleNamespace(exclude_none=True))
    dump.run(None, ctx)
    assert ctx.temp["response_payload"] == {"B": 1, "extra": 2}
