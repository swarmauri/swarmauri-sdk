from __future__ import annotations

from tigrbl_core._spec.io_spec import IOSpec, Pair


def test_assemble_returns_new_spec_with_assemble_cfg() -> None:
    spec = IOSpec().assemble(("first", "last"), lambda payload, ctx: payload | ctx)

    assert spec._assemble is not None
    assert spec._assemble.sources == ("first", "last")


def test_paired_caches_and_restores_stored_value() -> None:
    io = IOSpec().paired(lambda _: Pair(raw="raw", stored="stored"), alias="token")
    ctx = {"temp": {}}

    assert io._paired is not None
    assert io._paired.gen(ctx) == "raw"

    class Ctx:
        temp = ctx["temp"]

    assert io._paired.store("raw", Ctx()) == "stored"


def test_alias_readtime_appends_alias_configs() -> None:
    io = IOSpec().alias_readtime("masked", lambda obj, ctx: f"{obj}:{ctx['x']}")

    assert len(io._readtime_aliases) == 1
    assert io._readtime_aliases[0].name == "masked"
