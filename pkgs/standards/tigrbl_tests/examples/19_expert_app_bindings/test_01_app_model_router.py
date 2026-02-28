"""Lesson 19: app-level model router binding.

TigrblApp aggregates model routers so the application can manage REST routes
per model through its namespace. This pattern is preferred because it keeps
the app aware of generated routers without manual tracking.
"""

from tigrbl import TableBase, TigrblApp
from tigrbl.shortcuts.engine import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String


def test_app_binding_attaches_model_router():
    """Including a model stores its router in the app router registry."""

    class Widget(TableBase, GUIDPk):
        __tablename__ = "lesson_app_router"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    app = TigrblApp(engine=mem(async_=False))

    _, router = app.include_table(Widget)

    assert router is not None
    assert app.routers[Widget.__name__] is router


def test_app_router_registry_keeps_model_name():
    """Router registry keys align with model names for easy discovery."""

    class Widget(TableBase, GUIDPk):
        __tablename__ = "lesson_app_router_registry"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    app = TigrblApp(engine=mem(async_=False))

    _, router = app.include_table(Widget)

    assert Widget.__name__ in app.routers
    assert app.routers[Widget.__name__] is router
