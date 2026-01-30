from tigrbl import hook_ctx
from tigrbl.hook import HOOK_DECLS_ATTR
from tigrbl.op.decorators import _unwrap


def test_hook_ctx_attaches_declarations():
    @hook_ctx(ops="*", phase="PRE_HANDLER")
    def audit(cls, ctx):
        return None

    assert hasattr(_unwrap(audit), HOOK_DECLS_ATTR)
