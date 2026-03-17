"""Lesson 07.4: Scoping hooks to specific operations."""

from tigrbl import TableBase, TigrblApp, hook_ctx
from tigrbl.shortcuts.engine import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String


def test_hook_scopes_apply_to_specific_ops():
    """Explain that scoped hooks attach only to the declared operations.

    Purpose: show that a hook targeting read/update attaches to each of those
    phases without affecting other operations.
    Design practice: scope hooks narrowly to limit coupling across endpoints.
    """

    # Setup: attach the hook to a model so binding can collect it.
    class LessonHookScope(TableBase, GUIDPk):
        __tablename__ = "lesson_hook_scope"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

        # Setup: declare the hook for read/update in the class body.
        @hook_ctx(ops=("read", "update"), phase="POST_RESPONSE")
        def audit(cls, ctx):
            return None

    # Deployment: include the model in an app and bind to build hook registries.
    app = TigrblApp(engine=mem(async_=False))
    app.include_table(LessonHookScope)
    app.initialize()
    app.bind(LessonHookScope)

    # Test: inspect the hook registries for read/update.
    read_hooks = LessonHookScope.hooks.read.POST_RESPONSE
    update_hooks = LessonHookScope.hooks.update.POST_RESPONSE

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
    class LessonHookScopeIsolation(TableBase, GUIDPk):
        __tablename__ = "lesson_hook_scope_isolation"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

        # Setup: declare the hook for read/update in the class body.
        @hook_ctx(ops=("read", "update"), phase="PRE_HANDLER")
        def audit(cls, ctx):
            return None

    # Deployment: bind the model in an app to populate hook registries.
    app = TigrblApp(engine=mem(async_=False))
    app.include_table(LessonHookScopeIsolation)
    app.initialize()
    app.bind(LessonHookScopeIsolation)

    # Test: check whether create has any PRE_HANDLER hooks.
    create_hooks = getattr(
        getattr(LessonHookScopeIsolation.hooks, "create", None), "PRE_HANDLER", []
    )

    # Assertion: create has no hooks because it was not listed.
    assert create_hooks == []
