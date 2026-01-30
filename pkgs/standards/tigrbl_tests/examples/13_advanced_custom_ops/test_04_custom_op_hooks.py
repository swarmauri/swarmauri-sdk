from tigrbl import Base, TigrblApp, hook_ctx, op_ctx
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String


def test_custom_op_hooks_register():
    """Explain how hooks bind to custom ops.

    Purpose:
        Demonstrate that hooks declared with ``hook_ctx`` attach to custom ops
        once the API binds the model.

    What this shows:
        - Custom op names can be targeted by hook declarations.
        - Hook registries are populated during binding.

    Best practice:
        Keep hook registration explicit and scoped to the op alias to avoid
        unintended side effects.
    """

    # Setup: define a model and a custom op that will be hooked.
    class Widget(Base, GUIDPk):
        __tablename__ = "lesson_custom_hook_widgets"
        __allow_unmapped__ = True
        name = Column(String, nullable=False)

    @op_ctx(alias="report", target="custom", arity="collection")
    def report(cls, ctx):
        return [{"report": True}]

    @hook_ctx(ops="report", phase="POST_RESPONSE")
    def audit(cls, ctx):
        return None

    # Setup: attach the op and hook to the model.
    Widget.report = report
    Widget.audit = audit

    # Deployment: include the model in the API so hooks are bound.
    api = TigrblApp(engine=mem(async_=False))
    api.include_model(Widget)
    api.initialize()

    # Test: bind the model to populate hook registries.
    api.bind(Widget)

    # Assertion: the POST_RESPONSE hook is registered for the custom op.
    assert len(getattr(Widget.hooks, "report").POST_RESPONSE) == 1


def test_custom_op_hooks_can_register_multiple_phases():
    """Show hooks can target multiple phases for a single op.

    Purpose:
        Verify that separate hooks for different phases are collected under
        the same custom op namespace.

    What this shows:
        - Hook groups are per-op and per-phase.
        - Multiple hooks can coexist without overwriting each other.

    Best practice:
        Split hooks by phase to keep side effects isolated (e.g., audit vs.
        post-processing) and easier to test.
    """

    # Setup: define a model and a custom op with multiple hooks.
    class Widget(Base, GUIDPk):
        __tablename__ = "lesson_custom_hook_phases_widgets"
        __allow_unmapped__ = True
        name = Column(String, nullable=False)

    @op_ctx(alias="report", target="custom", arity="collection")
    def report(cls, ctx):
        return [{"report": True}]

    @hook_ctx(ops="report", phase="PRE_HANDLER")
    def prepare(cls, ctx):
        return None

    @hook_ctx(ops="report", phase="POST_RESPONSE")
    def audit(cls, ctx):
        return None

    # Setup: attach the op and hooks to the model.
    Widget.report = report
    Widget.prepare = prepare
    Widget.audit = audit

    # Deployment: include the model so hooks bind with the API.
    api = TigrblApp(engine=mem(async_=False))
    api.include_model(Widget)
    api.initialize()

    # Test: bind the model and inspect hook phases.
    api.bind(Widget)
    hooks = getattr(Widget.hooks, "report")

    # Assertion: hooks for both phases are present and distinct.
    assert len(hooks.PRE_HANDLER) == 1
    assert len(hooks.POST_RESPONSE) == 1
