from tigrbl.config.constants import HOOK_DECLS_ATTR
from tigrbl.hook.decorators import hook_ctx
from tigrbl.hook.hook_spec import HookSpec
from tigrbl.hook.shortcuts import hook, hook_spec


def _step(ctx):
    return ctx


def test_hook_spec_and_shortcuts():
    spec = hook_spec("PRE_HANDLER", _step, order=5, name="sample", description="demo")
    assert isinstance(spec, HookSpec)
    assert spec.phase == "PRE_HANDLER"
    assert spec.fn is _step
    assert spec.order == 5
    assert spec.name == "sample"
    assert spec.description == "demo"

    hook_obj = hook("POST_HANDLER", "read", _step, name="hook", description="desc")
    assert hook_obj.phase == "POST_HANDLER"
    assert hook_obj.ops == "read"


def test_hook_ctx_decorator_binds_decl():
    @hook_ctx("read", phase="PRE_HANDLER")
    def pre_hook(cls, ctx):
        return ctx

    wrapped = pre_hook.__func__
    decls = getattr(wrapped, HOOK_DECLS_ATTR)
    assert len(decls) == 1
    assert decls[0].phase == "PRE_HANDLER"
    assert decls[0].ops == "read"
    assert getattr(wrapped, "__tigrbl_ctx_only__") is True
