from types import SimpleNamespace

from autoapi.v3.runtime.atoms.schema import collect_in


class Storage:
    def __init__(self) -> None:
        self.nullable = False


class Col:
    def __init__(self) -> None:
        self.storage = Storage()
        self.alias_in = "alias"


class VirtCol:
    storage = None


def test_collect_in_builds_schema() -> None:
    specs = {"name": Col(), "v": VirtCol()}
    ctx = SimpleNamespace(specs=specs, op="create", temp={})
    collect_in.run(None, ctx)
    schema = ctx.temp["schema_in"]
    assert schema["by_field"]["name"]["alias_in"] == "alias"
    assert "name" in schema["required"]
    assert schema["by_field"]["v"]["virtual"] is True
