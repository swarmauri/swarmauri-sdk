from types import SimpleNamespace

from autoapi.v3.runtime.atoms.schema import collect_out


class Storage:
    def __init__(self) -> None:
        self.nullable = True


class Col:
    def __init__(self) -> None:
        self.storage = Storage()
        self.alias_out = "alias"
        self.sensitive = True


def test_collect_out_registers_alias_and_sensitivity() -> None:
    specs = {"name": Col()}
    ctx = SimpleNamespace(specs=specs, temp={})
    collect_out.run(None, ctx)
    schema = ctx.temp["schema_out"]
    assert schema["aliases"]["name"] == "alias"
    assert schema["by_field"]["name"]["sensitive"] is True
    assert "name" in schema["expose"]


def test_collect_out_runs_only_once() -> None:
    specs = {"name": Col()}
    ctx = SimpleNamespace(specs=specs, temp={})
    collect_out.run(None, ctx)
    ctx.specs = {"other": Col()}
    collect_out.run(None, ctx)
    schema = ctx.temp["schema_out"]
    assert "name" in schema["by_field"]
    assert "other" not in schema["by_field"]
