"""Lesson 16: table router bindings.

This lesson highlights how REST routers are stored on the API instance so
handlers can be discovered and composed without inspecting the FastAPI app.
The router registry is the preferred pattern because it centralizes routing
metadata with the API configuration.
"""

from tigrbl import Base, TigrblApi
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String


def test_table_binding_attaches_rest_router():
    """REST routers returned by include_model are stored on the API namespace."""

    class LessonTableRouter(Base, GUIDPk):
        __tablename__ = "lessontablerouters"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    Widget = LessonTableRouter
    api = TigrblApi(engine=mem(async_=False))

    _, router = api.include_model(Widget)

    assert router is not None
    assert api.routers[Widget.__name__] is router


def test_router_registry_tracks_model_alias():
    """The router registry can be queried by model name for routing metadata."""

    class LessonTableRouterRegistry(Base, GUIDPk):
        __tablename__ = "lessontablerouterregistrys"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    Widget = LessonTableRouterRegistry
    api = TigrblApi(engine=mem(async_=False))

    _, router = api.include_model(Widget)

    assert Widget.__name__ in api.routers
    assert api.routers[Widget.__name__] is router
