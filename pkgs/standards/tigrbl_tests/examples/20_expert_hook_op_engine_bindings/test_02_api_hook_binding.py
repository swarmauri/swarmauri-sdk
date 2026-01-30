"""Lesson 20: API hook bindings.

API-level hook declarations merge into the model hook namespace when models
are included. This pattern is preferred because it enables cross-cutting
behavior (like auditing) to be configured once at the API layer.
"""

from tigrbl import Base, TigrblApi
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String


def test_api_hook_binding_merges_into_model():
    """API hooks should populate the model's hook namespace."""

    def audit(cls, ctx):
        return None

    api_hooks = {"*": {"PRE_HANDLER": [audit]}}
    api = TigrblApi(engine=mem(async_=False), api_hooks=api_hooks)

    class LessonApiHookBinding(Base, GUIDPk):
        __tablename__ = "lessonapihookbindings"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    Widget = LessonApiHookBinding

    api.include_model(Widget)

    hooks = Widget.hooks.create.PRE_HANDLER
    assert any(step.__name__ == "audit" for step in hooks)


def test_api_hook_binding_respects_alias_namespace():
    """Merged hooks should appear under the model's alias namespace."""

    def audit(cls, ctx):
        return None

    api_hooks = {"*": {"PRE_HANDLER": [audit]}}
    api = TigrblApi(engine=mem(async_=False), api_hooks=api_hooks)

    class LessonApiHookAliasBinding(Base, GUIDPk):
        __tablename__ = "lessonapihookaliasbindings"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

    Widget = LessonApiHookAliasBinding

    api.include_model(Widget)

    assert isinstance(Widget.hooks.create.PRE_HANDLER, list)
