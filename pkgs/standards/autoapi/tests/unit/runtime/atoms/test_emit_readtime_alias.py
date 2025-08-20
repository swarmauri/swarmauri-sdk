from types import SimpleNamespace

from autoapi.v3.runtime.atoms.emit import readtime_alias


class Col:
    emit_alias = "hint"
    sensitive = True


def test_readtime_alias_masks_sensitive_value() -> None:
    specs = {"secret": Col()}
    temp = {"response_extras": {}, "emit_aliases": {"pre": [], "post": [], "read": []}}
    ctx = SimpleNamespace(specs=specs, temp=temp)
    obj = SimpleNamespace(secret="abcd1234")
    readtime_alias.run(obj, ctx)
    assert ctx.temp["response_extras"]["hint"] == "••••1234"
