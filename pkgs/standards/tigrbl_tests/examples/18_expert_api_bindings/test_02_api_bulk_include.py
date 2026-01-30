"""Lesson 18: bulk API inclusion.

Bulk inclusion binds multiple models to the API in a single operation. The
bulk workflow is preferred because it keeps API registration consistent when
bootstrapping a service with several models.
"""

from tigrbl import TigrblApi
from tigrbl.engine.shortcuts import mem

from examples._support import build_widget_model


def test_api_binding_includes_multiple_models():
    """include_models registers each model in the API registry."""
    Widget = build_widget_model("LessonApiBulkWidget")
    Gadget = build_widget_model("LessonApiBulkGadget")
    api = TigrblApi(engine=mem(async_=False))

    api.include_models([Widget, Gadget])

    assert {Widget.__name__, Gadget.__name__}.issubset(api.models)


def test_bulk_include_populates_schema_namespaces():
    """Bulk inclusion should create schema namespaces for each model."""
    Widget = build_widget_model("LessonApiBulkSchemaWidget")
    Gadget = build_widget_model("LessonApiBulkSchemaGadget")
    api = TigrblApi(engine=mem(async_=False))

    api.include_models([Widget, Gadget])

    assert hasattr(api.schemas, Widget.__name__)
    assert hasattr(api.schemas, Gadget.__name__)
