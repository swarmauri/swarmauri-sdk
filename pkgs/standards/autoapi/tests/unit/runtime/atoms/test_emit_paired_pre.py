from types import SimpleNamespace

from autoapi.v3.runtime.atoms.emit import paired_pre


def test_paired_pre_records_descriptor() -> None:
    temp = {"paired_values": {"token": {"raw": "abc", "alias": "t"}}}
    ctx = SimpleNamespace(persist=True, specs={}, temp=temp)
    paired_pre.run(None, ctx)
    pre = ctx.temp["emit_aliases"]["pre"]
    assert pre[0]["field"] == "token"
    assert pre[0]["alias"] == "t"
