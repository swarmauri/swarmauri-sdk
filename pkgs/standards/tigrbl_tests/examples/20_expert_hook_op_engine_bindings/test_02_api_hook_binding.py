"""Lesson 20: API hook bindings.

API-level hook declarations merge into the model hook namespace when models
are included. This pattern is preferred because it enables cross-cutting
behavior (like auditing) to be configured once at the API layer.
"""

from tigrbl import TableBase, TigrblRouter
from tigrbl.shortcuts.engine import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String


def test_router_hook_binding_merges_into_model():
    """API hooks should populate the model's hook namespace."""

    def audit(cls, ctx):
        return None

    router_hooks = {"*": {"PRE_HANDLER": [audit]}}
    router = TigrblRouter(engine=mem(async_=False), router_hooks=router_hooks)

    class Widget(TableBase, GUIDPk):
        __tablename__ = "lesson_router_hook_binding"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    router.include_table(Widget)

    hooks = Widget.hooks.create.PRE_HANDLER
    assert any(step.__name__ == "audit" for step in hooks)


def test_router_hook_binding_respects_alias_namespace():
    """Merged hooks should appear under the model's alias namespace."""

    def audit(cls, ctx):
        return None

    router_hooks = {"*": {"PRE_HANDLER": [audit]}}
    router = TigrblRouter(engine=mem(async_=False), router_hooks=router_hooks)

    class Widget(TableBase, GUIDPk):
        __tablename__ = "lesson_router_hook_alias_binding"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    router.include_table(Widget)

    assert isinstance(Widget.hooks.create.PRE_HANDLER, list)
