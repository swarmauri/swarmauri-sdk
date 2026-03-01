"""Lesson 18: API namespaces.

API bindings populate dedicated namespaces (schemas, handlers, hooks, etc.)
so consumers can discover generated artifacts through attribute access. This
pattern is preferred because it keeps generated bindings grouped by model name
and avoids leaking implementation details into unrelated modules.
"""

from tigrbl import Base, TigrblRouter
from tigrbl.shortcuts.engine import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String


def test_router_binding_attaches_namespaces():
    """Including a model exposes schema and handler namespaces on the API."""

    class Widget(Base, GUIDPk):
        __tablename__ = "lesson_router_namespaces"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    router = TigrblRouter(engine=mem(async_=False))

    router.include_table(Widget)

    assert hasattr(router.schemas, Widget.__name__)
    assert hasattr(router.handlers, Widget.__name__)


def test_router_namespace_entries_are_model_scoped():
    """Namespace attributes are keyed by model name for clear introspection."""

    class Widget(Base, GUIDPk):
        __tablename__ = "lesson_router_namespaces_scoped"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    router = TigrblRouter(engine=mem(async_=False))

    router.include_table(Widget)

    assert Widget.__name__ in router.schemas.__dict__
    assert Widget.__name__ in router.handlers.__dict__
