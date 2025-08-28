from types import SimpleNamespace

from autoapi.v3.runtime.atoms.refresh import demand


class Storage:
    def __init__(self) -> None:
        self.server_default = True
        self.autoincrement = False
        self.primary_key = False


class Col:
    def __init__(self) -> None:
        self.storage = Storage()


def test_refresh_demand_marks_need() -> None:
    ctx = SimpleNamespace(
        persist=True, specs={"id": Col()}, temp={}, cfg=SimpleNamespace()
    )
    demand.run(None, ctx)
    assert ctx.temp["refresh_demand"] is True
    assert ctx.temp["refresh_fields"] == ("id",)
