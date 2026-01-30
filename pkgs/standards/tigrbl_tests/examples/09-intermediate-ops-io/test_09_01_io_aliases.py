from __future__ import annotations

from tigrbl.specs import IO


def test_io_spec_aliases() -> None:
    spec = IO(alias_in="nickname", alias_out="display_name")
    assert spec.alias_in == "nickname"
    assert spec.alias_out == "display_name"
