from types import SimpleNamespace

from tigrbl_atoms.atoms.wire import build_in
from tigrbl.runtime.status.exceptions import HTTPException


def test_build_in_maps_alias_and_tracks_unknown() -> None:
    schema_in = {"by_field": {"name": {"alias_in": "n"}}}
    ctx = SimpleNamespace(
        temp={"schema_in": schema_in}, in_data={"n": "Bob", "extra": 1}
    )
    build_in._run(None, ctx)
    assert ctx.temp["in_values"] == {"name": "Bob"}
    assert ctx.temp["in_unknown"] == ("extra",)


def test_build_in_rejects_wrapper_keys_when_not_in_schema() -> None:
    schema_in = {"by_field": {"name": {"alias_in": "name"}}}
    ctx = SimpleNamespace(
        temp={"schema_in": schema_in},
        in_data={"data": {"name": "Wrapped"}},
    )

    try:
        build_in._run(None, ctx)
    except HTTPException as exc:
        assert exc.status_code == 422
        assert exc.detail["disallowed_keys"] == ["data"]
    else:  # pragma: no cover - safety
        raise AssertionError("Expected HTTPException for disallowed wrapper key")


def test_build_in_allows_wrapper_key_when_field_exists() -> None:
    schema_in = {"by_field": {"data": {"alias_in": "data"}}}
    ctx = SimpleNamespace(temp={"schema_in": schema_in}, in_data={"data": "ok"})

    build_in._run(None, ctx)

    assert ctx.temp["in_values"] == {"data": "ok"}
