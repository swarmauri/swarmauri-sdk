from tigrbl import App, hook_ctx
from tigrbl.config.constants import HOOK_DECLS_ATTR
from tigrbl.hook._hook import Hook


def _get_hook(fn) -> Hook:
    decls = getattr(fn, HOOK_DECLS_ATTR)
    assert len(decls) == 1
    return decls[0]


def test_hook_ctx_internal_binding_records_ctx_only_hook():
    class Widget:
        @hook_ctx("read", phase="POST_COMMIT")
        def after_read(cls, ctx):
            return None

    method = Widget.__dict__["after_read"]
    assert isinstance(method, classmethod)
    assert method.__func__.__tigrbl_ctx_only__ is True
    hook = _get_hook(method.__func__)
    assert hook.phase == "POST_COMMIT"
    assert hook.ops == "read"


def test_hook_ctx_external_binding_transfers_to_other_class():
    class Source:
        @hook_ctx(("create", "update"), phase="PRE_COMMIT")
        def before_change(cls, ctx):
            return None

    class ExampleApp(App):
        TITLE = "Example"
        VERSION = "0.1.0"
        LIFESPAN = None

    ExampleApp.before_change = Source.__dict__["before_change"]

    method = ExampleApp.__dict__["before_change"]
    assert isinstance(method, classmethod)
    hook = _get_hook(method.__func__)
    assert hook.ops == ("create", "update")
    assert hook.phase == "PRE_COMMIT"


def test_hook_ctx_binding_on_plain_function():
    @hook_ctx("delete", phase="POST_COMMIT")
    def cleanup(cls, ctx):
        return None

    hook = _get_hook(cleanup.__func__)
    assert hook.ops == "delete"
    assert hook.phase == "POST_COMMIT"
