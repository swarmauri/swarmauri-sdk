"""Lesson 07.2: Binding hooks onto models during API setup."""

from tigrbl import Base, TigrblApp, hook_ctx
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String


def test_model_hooks_bind_on_rebind():
    """Explain that hooks bind when the API binds or rebinds a model.

    Purpose: ensure hooks defined on the model are collected into the hook
    registry as part of `bind`, enabling automatic pipeline wiring.
    Design practice: register hooks on the model so binding remains declarative.
    """

    # Setup: declare a model with an inline hook for the create operation.
    class LessonHook(Base, GUIDPk):
        __tablename__ = "lesson_hooks"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

        # Setup: add the hook method directly on the model.
        @hook_ctx(ops="create", phase="POST_COMMIT")
        def notify(cls, ctx):
            return None

    # Deployment: include the model in an app so binding occurs.
    api = TigrblApp(engine=mem(async_=False))
    api.include_model(LessonHook)
    api.initialize()
    api.bind(LessonHook)

    # Test: read the bound hook registry for the create op and phase.
    hooks = LessonHook.__tigrbl_hooks__["create"]["POST_COMMIT"]

    # Assertion: one hook is registered for the create/POST_COMMIT slot.
    assert len(hooks) == 1


def test_model_hook_scopes_do_not_leak_to_other_ops():
    """Show that hook scopes are isolated to the declared ops.

    Purpose: confirm that a hook bound to "create" does not appear on "update".
    Design practice: scope hooks narrowly to avoid unintended side effects.
    """

    # Setup: define the model with a hook scoped only to create.
    class LessonHookScopeIsolation(Base, GUIDPk):
        __tablename__ = "lesson_hook_scope_isolation"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

        # Setup: attach the hook directly in the class body.
        @hook_ctx(ops="create", phase="PRE_HANDLER")
        def notify(cls, ctx):
            return None

    # Deployment: include the model and bind hooks through the app.
    api = TigrblApp(engine=mem(async_=False))
    api.include_model(LessonHookScopeIsolation)
    api.initialize()
    api.bind(LessonHookScopeIsolation)

    # Test: check hook registries for create vs update ops.
    create_hooks = LessonHookScopeIsolation.__tigrbl_hooks__["create"]["PRE_HANDLER"]
    update_hooks = LessonHookScopeIsolation.__tigrbl_hooks__.get("update", {}).get(
        "PRE_HANDLER", []
    )

    # Assertion: create has a hook, update remains untouched.
    assert len(create_hooks) == 1
    assert update_hooks == []
