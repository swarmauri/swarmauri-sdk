from __future__ import annotations

from tigrbl_core._spec.router_spec import RouterSpec


def test_router_spec_defaults() -> None:
    spec = RouterSpec()

    assert spec.name == "router"
    assert spec.prefix == ""
    assert spec.tags == ()
    assert spec.ops == ()


def test_router_spec_custom_values() -> None:
    spec = RouterSpec(name="api", prefix="/v1", tags=("core",), tables=("users",))

    assert spec.name == "api"
    assert spec.prefix == "/v1"
    assert spec.tags == ("core",)
    assert spec.tables == ("users",)
