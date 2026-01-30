"""Lesson 18: diagnostics router mounting.

Diagnostics routers provide operational visibility for an API. The router is
retrieved from the API instance and mounted on a host app, keeping the API
responsible for its own diagnostic endpoints.
"""

from tigrbl import App, TigrblApi
from tigrbl.engine.shortcuts import mem

from examples._support import build_widget_model


def test_api_binding_mounts_diagnostics_router():
    """attach_diagnostics returns a router that can be mounted on an app."""
    Widget = build_widget_model("LessonApiDiagnostics")
    api = TigrblApi(engine=mem(async_=False))
    api.include_model(Widget)

    app = App()
    router = api.attach_diagnostics(app=app)

    assert router is not None


def test_api_diagnostics_mounts_on_app_namespace():
    """Diagnostics mounting should attach routes to the host app."""
    Widget = build_widget_model("LessonApiDiagnosticsHost")
    api = TigrblApi(engine=mem(async_=False))
    api.include_model(Widget)

    app = App()
    router = api.attach_diagnostics(app=app)

    assert router is not None
    assert any(
        route.path == f"{api.system_prefix}/healthz" for route in app.router.routes
    )
