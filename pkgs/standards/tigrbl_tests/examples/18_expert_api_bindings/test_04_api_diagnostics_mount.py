"""Lesson 18: diagnostics router mounting.

Diagnostics routers provide operational visibility for an API. The router is
retrieved from the API instance and mounted on a host app, keeping the API
responsible for its own diagnostic endpoints.
"""

from tigrbl import Base, TigrblRouter, TigrblApp
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String


def test_router_binding_mounts_diagnostics_router():
    """attach_diagnostics returns a router that can be mounted on an app."""

    class Widget(Base, GUIDPk):
        __tablename__ = "lesson_router_diagnostics"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    router = TigrblRouter(engine=mem(async_=False))
    router.include_table(Widget)

    app = TigrblApp()
    app.include_router(router)
    app.attach_diagnostics()

    assert router is not None


def test_router_diagnostics_mounts_on_app_namespace():
    """Diagnostics mounting should attach routes to the host app."""

    class Widget(Base, GUIDPk):
        __tablename__ = "lesson_router_diagnostics_host"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    router = TigrblRouter(engine=mem(async_=False))
    router.include_table(Widget)

    app = TigrblApp()
    app.include_router(router)
    app.attach_diagnostics()

    assert router is not None
    assert any(
        route.path == f"{app.system_prefix}/healthz" for route in app.router.routes
    )
