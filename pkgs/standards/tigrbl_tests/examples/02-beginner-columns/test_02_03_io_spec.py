from __future__ import annotations

from tigrbl.specs import IO


def test_io_spec_basics() -> None:
    spec = IO(
        in_verbs=("create", "update"),
        out_verbs=("read",),
        header_in="X-Request-ID",
        header_required_in=True,
    )
    assert spec.in_verbs == ("create", "update")
    assert spec.out_verbs == ("read",)
    assert spec.header_in == "X-Request-ID"
    assert spec.header_required_in is True
