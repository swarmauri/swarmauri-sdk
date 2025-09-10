from types import SimpleNamespace

from tigrbl.runtime.atoms.wire import build_in


def test_build_in_maps_alias_and_tracks_unknown() -> None:
    schema_in = {"by_field": {"name": {"alias_in": "n"}}}
    ctx = SimpleNamespace(
        temp={"schema_in": schema_in}, in_data={"n": "Bob", "extra": 1}
    )
    build_in.run(None, ctx)
    assert ctx.temp["in_values"] == {"name": "Bob"}
    assert ctx.temp["in_unknown"] == ("extra",)
