"""Lesson 07.4: Scoping hooks to specific operations."""

from tigrbl import Base, TigrblApp, hook_ctx
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String


def test_hook_scopes_apply_to_specific_ops():
    """Explain that scoped hooks attach only to the declared operations.

    Purpose: show that a hook targeting read/update attaches to each of those
    phases without affecting other operations.
    Design practice: scope hooks narrowly to limit coupling across endpoints.
    """

    # Setup: attach the hook to a model so binding can collect it.
    class LessonHookScope(Base, GUIDPk):
        __tablename__ = "lesson_hook_scope"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

        # Setup: declare the hook for read/update in the class body.
        @hook_ctx(ops=("read", "update"), phase="POST_RESPONSE")
        def audit(cls, ctx):
            return None

    # Deployment: include the model in an app and bind to build hook registries.
    api = TigrblApp(engine=mem(async_=False))
    api.include_model(LessonHookScope)
    api.initialize()
    api.bind(LessonHookScope)

    # Test: inspect the hook registries for read/update.
    read_hooks = LessonHookScope.__tigrbl_hooks__["read"]["POST_RESPONSE"]
    update_hooks = LessonHookScope.__tigrbl_hooks__["update"]["POST_RESPONSE"]

    # Assertion: both operations have a hook registered.
    assert len(read_hooks) == 1
    assert len(update_hooks) == 1


def test_hook_scopes_exclude_unlisted_ops():
    """Confirm unlisted operations remain untouched by scoped hooks.

    Purpose: prove the hook does not apply to "create" when only read/update are
    declared, reinforcing isolation.
    Design practice: use explicit scopes to prevent unintended side effects.
    """

    # Setup: attach the hook to a model class.
    class LessonHookScopeIsolation(Base, GUIDPk):
        __tablename__ = "lesson_hook_scope_isolation"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

        # Setup: declare the hook for read/update in the class body.
        @hook_ctx(ops=("read", "update"), phase="PRE_HANDLER")
        def audit(cls, ctx):
            return None

    # Deployment: bind the model in an app to populate hook registries.
    api = TigrblApp(engine=mem(async_=False))
    api.include_model(LessonHookScopeIsolation)
    api.initialize()
    api.bind(LessonHookScopeIsolation)

    # Test: check whether create has any PRE_HANDLER hooks.
    create_hooks = LessonHookScopeIsolation.__tigrbl_hooks__.get("create", {}).get(
        "PRE_HANDLER", []
    )

    # Assertion: create has no hooks because it was not listed.
    assert create_hooks == []
