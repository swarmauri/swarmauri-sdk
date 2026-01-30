from tigrbl import Base, TigrblApp, hook_ctx
from tigrbl.engine.shortcuts import mem
from tigrbl.orm.mixins import GUIDPk
from tigrbl.types import Column, String


def test_hook_sequence_merges_across_mro_on_api():
    """Explain hook ordering when models inherit from base classes.

    Purpose:
        Demonstrate that hook declarations on base and child models are merged
        and appear in order when bound through the API.

    What this shows:
        - Hook decorators are collected across the model MRO.
        - The API exposes merged hook chains for the bound model.

    Best practice:
        Keep shared hooks on base models and add specialized hooks on child
        models so the final hook chain is both reusable and explicit.
    """

    # Setup: declare a base mixin with a hook for the create operation.
    class BaseWidgetMixin:
        @hook_ctx(ops="create", phase="PRE_COMMIT")
        def base_audit(cls, ctx):
            return None

    # Setup: declare a concrete model with a child hook.
    class ChildWidget(BaseWidgetMixin, Base, GUIDPk):
        __tablename__ = "hook_child_widgets"
        __allow_unmapped__ = True
        name = Column(String, nullable=False)

        @hook_ctx(ops="create", phase="PRE_COMMIT")
        def child_audit(cls, ctx):
            return None

    # Deployment: bind the child model through the API.
    api = TigrblApp(engine=mem(async_=False))
    api.include_model(ChildWidget)

    # Test: pull the merged hooks for the create operation.
    hooks_ns = getattr(api.hooks, ChildWidget.__name__)
    phase_hooks = hooks_ns.create.PRE_COMMIT
    hook_names = [hook.__name__ for hook in phase_hooks]

    # Assertion: the base hook appears before the child hook.
    assert hook_names == ["base_audit", "child_audit"]
