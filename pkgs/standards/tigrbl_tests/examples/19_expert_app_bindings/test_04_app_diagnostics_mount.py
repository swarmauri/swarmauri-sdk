"""Lesson 19: diagnostics router mounting for apps.

Diagnostics endpoints are mounted on a host app while the TigrblApp manages
their construction. The design keeps diagnostic routes colocated with app
configuration and avoids manual router wiring.
"""

from tigrbl import App, Base, TigrblApp
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String


def test_app_binding_mounts_diagnostics_router():
    """attach_diagnostics returns the diagnostics router for mounting."""

    class LessonAppDiagnostics(Base, GUIDPk):
        __tablename__ = "lessonappdiagnosticss"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    Widget = LessonAppDiagnostics
    app = TigrblApp(engine=mem(async_=False))
    app.include_model(Widget)

    host = App()
    router = app.attach_diagnostics(app=host)

    assert router is not None


def test_app_diagnostics_attach_to_host_routes():
    """Diagnostics routing should be attached to the host FastAPI app."""

    class LessonAppDiagnosticsHost(Base, GUIDPk):
        __tablename__ = "lessonappdiagnosticshosts"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    Widget = LessonAppDiagnosticsHost
    app = TigrblApp(engine=mem(async_=False))
    app.include_model(Widget)

    host = App()
    router = app.attach_diagnostics(app=host)

    assert router is not None
    assert any(
        route.path == f"{app.system_prefix}/healthz" for route in host.router.routes
    )
