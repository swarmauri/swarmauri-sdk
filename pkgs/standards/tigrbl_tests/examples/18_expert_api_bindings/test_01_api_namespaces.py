"""Lesson 18: API namespaces.

API bindings populate dedicated namespaces (schemas, handlers, hooks, etc.)
so consumers can discover generated artifacts through attribute access. This
pattern is preferred because it keeps generated bindings grouped by model name
and avoids leaking implementation details into unrelated modules.
"""

from tigrbl import Base, TigrblApi
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String


def test_api_binding_attaches_namespaces():
    """Including a model exposes schema and handler namespaces on the API."""

    class LessonApiNamespaces(Base, GUIDPk):
        __tablename__ = "lessonapinamesspacess"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    Widget = LessonApiNamespaces
    api = TigrblApi(engine=mem(async_=False))

    api.include_model(Widget)

    assert hasattr(api.schemas, Widget.__name__)
    assert hasattr(api.handlers, Widget.__name__)


def test_api_namespace_entries_are_model_scoped():
    """Namespace attributes are keyed by model name for clear introspection."""

    class LessonApiNamespacesScoped(Base, GUIDPk):
        __tablename__ = "lessonapinamesspacesscoped"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    Widget = LessonApiNamespacesScoped
    api = TigrblApi(engine=mem(async_=False))

    api.include_model(Widget)

    assert Widget.__name__ in api.schemas.__dict__
    assert Widget.__name__ in api.handlers.__dict__
