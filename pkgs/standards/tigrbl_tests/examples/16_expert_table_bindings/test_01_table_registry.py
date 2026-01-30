"""Lesson 16: table registry bindings.

This lesson shows how table metadata is registered on an API instance so
consumers can discover model tables via the API's namespace rather than
recreating mapping logic themselves. The registry pattern keeps models and
tables aligned and makes it easy to reference the SQLAlchemy table object
directly from the API layer.
"""

from tigrbl import TigrblApi
from tigrbl.engine.shortcuts import mem

from examples._support import build_widget_model


def test_table_binding_registers_table_on_api():
    """The API table registry should map model names to SQLAlchemy tables."""
    Widget = build_widget_model("LessonTableRegistry")
    api = TigrblApi(engine=mem(async_=False))

    api.include_model(Widget)

    assert api.tables[Widget.__name__] is Widget.__table__


def test_table_registry_respects_model_identity():
    """The table registry keeps a stable reference for each model's table."""
    Widget = build_widget_model("LessonTableRegistryIdentity")
    api = TigrblApi(engine=mem(async_=False))

    api.include_model(Widget)

    assert Widget.__name__ in api.tables
    assert api.tables[Widget.__name__].name == Widget.__table__.name
