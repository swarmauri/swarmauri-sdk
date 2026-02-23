"""Lesson 07.3: Ordering multiple hooks in the same phase."""

from tigrbl import Base, TigrblApp, hook_ctx
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String


def test_hook_order_collects_multiple_hooks():
    """Explain that hooks for the same phase are all collected.

    Purpose: show multiple hook functions can share a phase and op.
    Design practice: split responsibilities across hooks to keep each focused.
    """

    # Setup: attach two hooks to a model class for the same phase.
    class LessonHookOrder(Base, GUIDPk):
        __tablename__ = "lesson_hook_order"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

        # Setup: define hook methods in declaration order.
        @hook_ctx(ops="create", phase="PRE_HANDLER")
        def first(cls, ctx):
            return None

        @hook_ctx(ops="create", phase="PRE_HANDLER")
        def second(cls, ctx):
            return None

    # Deployment: bind the model in an app to materialize hook registries.
    api = TigrblApp(engine=mem(async_=False))
    api.include_model(LessonHookOrder)
    api.initialize()
    api.bind(LessonHookOrder)

    # Test: read the PRE_HANDLER hooks for create.
    hooks = LessonHookOrder.__tigrbl_hooks__["create"]["PRE_HANDLER"]

    # Assertion: both hooks are registered.
    assert len(hooks) == 2


def test_hook_order_preserves_declaration_sequence():
    """Confirm hooks are evaluated in declaration order.

    Purpose: demonstrate that hook ordering is deterministic, which matters when
    hooks perform dependent work.
    Design practice: keep order explicit and documented to avoid surprises.
    """

    # Setup: attach ordered hooks to a model so the binder can collect them.
    class LessonHookOrderSequence(Base, GUIDPk):
        __tablename__ = "lesson_hook_order_sequence"
        __allow_unmapped__ = True

        name = Column(String, nullable=False)

        # Setup: define hook methods in declaration order.
        @hook_ctx(ops="create", phase="PRE_HANDLER")
        def first(cls, ctx):
            return None

        @hook_ctx(ops="create", phase="PRE_HANDLER")
        def second(cls, ctx):
            return None

    # Deployment: include the model in the app and bind hooks.
    api = TigrblApp(engine=mem(async_=False))
    api.include_model(LessonHookOrderSequence)
    api.initialize()
    api.bind(LessonHookOrderSequence)

    # Test: inspect hook ordering for the create PRE_HANDLER phase.
    hooks = LessonHookOrderSequence.__tigrbl_hooks__["create"]["PRE_HANDLER"]

    # Assertion: hook sequence matches the declaration order.
    assert hooks[0].__name__ == "first"
    assert hooks[1].__name__ == "second"
