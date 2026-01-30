"""Lesson 19: bulk model inclusion for apps.

Including multiple models at once ensures the application registry is fully
populated before startup. This is the preferred pattern for bootstrapping
larger apps because it keeps model configuration centralized.
"""

from tigrbl import Base, TigrblApp
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String


def test_app_binding_includes_multiple_models():
    """Bulk inclusion registers each model on the app registry."""

    class LessonAppBulkWidget(Base, GUIDPk):
        __tablename__ = "lessonappbulkwidgets"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    class LessonAppBulkGadget(Base, GUIDPk):
        __tablename__ = "lessonappbulkgadgets"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    Widget = LessonAppBulkWidget
    Gadget = LessonAppBulkGadget
    app = TigrblApp(engine=mem(async_=False))

    app.include_models([Widget, Gadget])

    assert {Widget.__name__, Gadget.__name__}.issubset(app.models)


def test_app_model_registry_exposes_named_entries():
    """The model registry retains a direct mapping from name to class."""

    class LessonAppBulkWidgetName(Base, GUIDPk):
        __tablename__ = "lessonappbulkwidgetnames"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    class LessonAppBulkGadgetName(Base, GUIDPk):
        __tablename__ = "lessonappbulkgadgetnames"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    Widget = LessonAppBulkWidgetName
    Gadget = LessonAppBulkGadgetName
    app = TigrblApp(engine=mem(async_=False))

    app.include_models([Widget, Gadget])

    assert app.models[Widget.__name__] is Widget
    assert app.models[Gadget.__name__] is Gadget
