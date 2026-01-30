"""Lesson 19: bulk model inclusion for apps.

Including multiple models at once ensures the application registry is fully
populated before startup. This is the preferred pattern for bootstrapping
larger apps because it keeps model configuration centralized.
"""

from tigrbl import TigrblApp
from tigrbl.engine.shortcuts import mem

from examples._support import build_widget_model


def test_app_binding_includes_multiple_models():
    """Bulk inclusion registers each model on the app registry."""
    Widget = build_widget_model("LessonAppBulkWidget")
    Gadget = build_widget_model("LessonAppBulkGadget")
    app = TigrblApp(engine=mem(async_=False))

    app.include_models([Widget, Gadget])

    assert {Widget.__name__, Gadget.__name__}.issubset(app.models)


def test_app_model_registry_exposes_named_entries():
    """The model registry retains a direct mapping from name to class."""
    Widget = build_widget_model("LessonAppBulkWidgetName")
    Gadget = build_widget_model("LessonAppBulkGadgetName")
    app = TigrblApp(engine=mem(async_=False))

    app.include_models([Widget, Gadget])

    assert app.models[Widget.__name__] is Widget
    assert app.models[Gadget.__name__] is Gadget
