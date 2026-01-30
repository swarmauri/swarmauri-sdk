"""Lesson 19: app-level model router binding.

TigrblApp aggregates model routers so the application can manage REST routes
per model through its namespace. This pattern is preferred because it keeps
the app aware of generated routers without manual tracking.
"""

from tigrbl import TigrblApp
from tigrbl.engine.shortcuts import mem

from examples._support import build_widget_model


def test_app_binding_attaches_model_router():
    """Including a model stores its router in the app router registry."""
    Widget = build_widget_model("LessonAppRouter")
    app = TigrblApp(engine=mem(async_=False))

    _, router = app.include_model(Widget)

    assert router is not None
    assert app.routers[Widget.__name__] is router


def test_app_router_registry_keeps_model_name():
    """Router registry keys align with model names for easy discovery."""
    Widget = build_widget_model("LessonAppRouterRegistry")
    app = TigrblApp(engine=mem(async_=False))

    _, router = app.include_model(Widget)

    assert Widget.__name__ in app.routers
    assert app.routers[Widget.__name__] is router
