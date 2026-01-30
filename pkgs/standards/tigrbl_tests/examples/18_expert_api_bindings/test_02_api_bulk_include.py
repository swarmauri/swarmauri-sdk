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

    class LessonApiBulkWidget(Base, GUIDPk):
        __tablename__ = "lessonapibulkwidgets"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    class LessonApiBulkGadget(Base, GUIDPk):
        __tablename__ = "lessonapibulkgadgets"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    Widget = LessonApiBulkWidget
    Gadget = LessonApiBulkGadget
    api = TigrblApi(engine=mem(async_=False))

    api.include_models([Widget, Gadget])

    assert {Widget.__name__, Gadget.__name__}.issubset(api.models)


def test_bulk_include_populates_schema_namespaces():
    """Bulk inclusion should create schema namespaces for each model."""

    class LessonApiBulkSchemaWidget(Base, GUIDPk):
        __tablename__ = "lessonapibulkschemawidgets"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    class LessonApiBulkSchemaGadget(Base, GUIDPk):
        __tablename__ = "lessonapibulkschemagadgets"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    Widget = LessonApiBulkSchemaWidget
    Gadget = LessonApiBulkSchemaGadget
    api = TigrblApi(engine=mem(async_=False))

    api.include_models([Widget, Gadget])

    assert hasattr(api.schemas, Widget.__name__)
    assert hasattr(api.schemas, Gadget.__name__)
