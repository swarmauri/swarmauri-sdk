"""Lesson 16: table model registry bindings.

This module focuses on the API model registry, which acts as a canonical
lookup table for ORM classes. Storing models by name lets other subsystems
discover model-level metadata without duplicating model discovery logic.
"""

from tigrbl import Base, TigrblApi
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String


def test_table_binding_registers_model():
    """Models included in the API are available via the models namespace."""

    class LessonTableModel(Base, GUIDPk):
        __tablename__ = "lessontablemodels"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    Widget = LessonTableModel
    api = TigrblApi(engine=mem(async_=False))

    api.include_model(Widget)

    assert api.models[Widget.__name__] is Widget


def test_model_registry_supports_multiple_models():
    """The API model registry should track multiple models by name."""

    class LessonTableModelPrimary(Base, GUIDPk):
        __tablename__ = "lessontablemodelprimarys"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    class LessonTableModelSecondary(Base, GUIDPk):
        __tablename__ = "lessontablemodelsecondarys"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    Widget = LessonTableModelPrimary
    Gadget = LessonTableModelSecondary
    api = TigrblApi(engine=mem(async_=False))

    api.include_model(Widget)
    api.include_model(Gadget)

    assert api.models[Widget.__name__] is Widget
    assert api.models[Gadget.__name__] is Gadget
