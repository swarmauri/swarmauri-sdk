"""Lesson 07.1: Declaring ctx-only hooks with `hook_ctx`."""

from tigrbl import hook_ctx
from tigrbl.hook import HOOK_DECLS_ATTR


def test_hook_ctx_attaches_declarations():
    """Explain how hook declarations are attached to the function object.

    Purpose: show that decorators register hook metadata on the underlying
    callable so the binder can collect them later.
    Design practice: keep hooks declarative and scoped to precise phases.
    """

    # Setup: declare a hook for all ops during PRE_HANDLER.
    @hook_ctx(ops="*", phase="PRE_HANDLER")
    def audit(cls, ctx):
        return None

    # Test: inspect the underlying function for hook declarations.
    declarations = getattr(audit.__func__, HOOK_DECLS_ATTR, None)

    # Assertion: the hook decorator attached declaration metadata.
    assert declarations is not None


def test_hook_ctx_supports_multiple_phase_declarations():
    """Demonstrate stacking hook decorators for different phases.

    Purpose: verify that multiple hook declarations can be attached to a single
    callable, enabling re-use without duplicating logic.
    Design practice: keep hook logic small and composable to reduce divergence.
    """

    # Setup: stack decorators to register the same callable in two phases.
    @hook_ctx(ops="create", phase="PRE_HANDLER")
    @hook_ctx(ops="read", phase="POST_RESPONSE")
    def audit(cls, ctx):
        return None

    # Test: capture the hook declarations from the function metadata.
    decls = getattr(audit.__func__, HOOK_DECLS_ATTR)

    # Assertion: both declarations are recorded for the single callable.
    assert len(decls) == 2
