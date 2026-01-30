"""Lesson 18: bulk API inclusion.

Bulk inclusion binds multiple models to the API in a single operation. The
bulk workflow is preferred because it keeps API registration consistent when
bootstrapping a service with several models.
"""

from tigrbl import Base, TigrblApi
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String


def test_api_binding_includes_multiple_models():
    """include_models registers each model in the API registry."""

    class Widget(Base, GUIDPk):
        __tablename__ = "lesson_api_bulk_widget"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    class Gadget(Base, GUIDPk):
        __tablename__ = "lesson_api_bulk_gadget"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    api = TigrblApi(engine=mem(async_=False))

    api.include_models([Widget, Gadget])

    assert {Widget.__name__, Gadget.__name__}.issubset(api.models)


def test_bulk_include_populates_schema_namespaces():
    """Bulk inclusion should create schema namespaces for each model."""

    class Widget(Base, GUIDPk):
        __tablename__ = "lesson_api_bulk_schema_widget"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    class Gadget(Base, GUIDPk):
        __tablename__ = "lesson_api_bulk_schema_gadget"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    api = TigrblApi(engine=mem(async_=False))

    api.include_models([Widget, Gadget])

    assert hasattr(api.schemas, Widget.__name__)
    assert hasattr(api.schemas, Gadget.__name__)
