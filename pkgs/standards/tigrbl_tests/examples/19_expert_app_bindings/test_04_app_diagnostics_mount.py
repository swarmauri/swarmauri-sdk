from tigrbl import TigrblApp
from tigrbl.engine.shortcuts import mem
from tigrbl.types import App

from examples._support import build_widget_model


def test_app_binding_mounts_diagnostics_router():
    """attach_diagnostics returns the diagnostics router for mounting."""
    Widget = build_widget_model("LessonAppDiagnostics")
    app = TigrblApp(engine=mem(async_=False))
    app.include_model(Widget)

    host = App()
    router = app.attach_diagnostics(app=host)

    assert router is not None


def test_app_diagnostics_attach_to_host_routes():
    """Diagnostics routing should be attached to the host FastAPI app."""
    Widget = build_widget_model("LessonAppDiagnosticsHost")
    app = TigrblApp(engine=mem(async_=False))
    app.include_model(Widget)

    host = App()
    router = app.attach_diagnostics(app=host)

    assert router is not None
    assert any(
        route.path == f"{app.system_prefix}/healthz" for route in host.router.routes
    )
