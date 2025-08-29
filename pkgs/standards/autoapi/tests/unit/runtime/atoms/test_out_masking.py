from types import SimpleNamespace

from autoapi.v3.runtime.atoms.out import masking


class SensitiveCol:
    sensitive = True


class PlainCol:
    sensitive = False


def test_out_masking_applies_to_sensitive_fields() -> None:
    specs = {"secret": SensitiveCol(), "public": PlainCol()}
    temp = {
        "response_payload": {"secret": "abcd1234", "token": "abc", "public": "x"},
        "emit_aliases": {"pre": [], "post": [{"alias": "token"}], "read": []},
    }
    ctx = SimpleNamespace(specs=specs, temp=temp)
    masking.run(None, ctx)
    assert ctx.temp["response_payload"]["secret"] == "••••1234"
    assert ctx.temp["response_payload"]["token"] == "abc"
