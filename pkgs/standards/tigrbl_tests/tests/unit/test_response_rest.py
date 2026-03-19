from __future__ import annotations

from types import SimpleNamespace

import pytest

from tigrbl import TigrblApp
from tigrbl_concrete._mapping.router.include import include_table

from .response_utils import (
    RESPONSE_KINDS,
    build_model_for_jinja_response,
    build_model_for_response,
    build_model_for_response_non_alias,
    build_ping_model,
)


def test_response_rest_bindings_attached_to_table_router_and_app():
    Widget = build_ping_model()

    assert hasattr(Widget, "rest")
    assert getattr(Widget.rest, "router", None) is not None

    router = SimpleNamespace()
    include_table(router, Widget, mount_router=False)
    assert getattr(getattr(router, "rest", SimpleNamespace()), "Widget", None)
    assert "Widget" in getattr(router, "routers", {})

    app = TigrblApp()
    app.include_table(Widget)
    assert getattr(getattr(app, "rest", SimpleNamespace()), "Widget", None)
    assert "Widget" in getattr(app, "routers", {})


@pytest.mark.parametrize("kind", RESPONSE_KINDS)
def test_response_rest_alias_table_routes_materialized(kind, tmp_path):
    Widget, _ = build_model_for_response(kind, tmp_path)
    route_paths = {getattr(route, "path", None) for route in Widget.rest.router.routes}
    assert "/widget/download" in route_paths


@pytest.mark.parametrize("kind", RESPONSE_KINDS)
def test_response_rest_non_alias_table_routes_materialized(kind, tmp_path):
    Widget, _ = build_model_for_response_non_alias(kind, tmp_path)
    route_paths = {getattr(route, "path", None) for route in Widget.rest.router.routes}
    assert "/widget/download" in route_paths


def test_response_rest_alias_table_jinja_route_materialized(tmp_path):
    pytest.importorskip("jinja2")
    Widget = build_model_for_jinja_response(tmp_path)
    route_paths = {getattr(route, "path", None) for route in Widget.rest.router.routes}
    assert "/widget/download" in route_paths
