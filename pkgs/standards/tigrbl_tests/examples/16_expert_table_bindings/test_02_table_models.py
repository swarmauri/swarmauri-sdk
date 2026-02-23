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

    class Widget(Base, GUIDPk):
        __tablename__ = "lesson_table_model"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    api = TigrblApi(engine=mem(async_=False))

    api.include_model(Widget)

    assert api.models[Widget.__name__] is Widget


def test_model_registry_supports_multiple_models():
    """The API model registry should track multiple models by name."""

    class Widget(Base, GUIDPk):
        __tablename__ = "lesson_table_model_primary"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    class Gadget(Base, GUIDPk):
        __tablename__ = "lesson_table_model_secondary"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    api = TigrblApi(engine=mem(async_=False))

    api.include_model(Widget)
    api.include_model(Gadget)

    assert api.models[Widget.__name__] is Widget
    assert api.models[Gadget.__name__] is Gadget
