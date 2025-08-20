from autoapi.v3.decorators import hook_ctx, _HookDecl


def test_hook_ctx_marks_ctx_only():
    class Table:
        @hook_ctx(ops="create", phase="PRE_HANDLER")
        def before_create(cls, ctx):
            pass

    assert getattr(Table.before_create.__func__, "__autoapi_ctx_only__") is True


def test_hook_ctx_records_ops():
    class Table:
        @hook_ctx(ops=("create", "delete"), phase="PRE_HANDLER")
        def hook(cls, ctx):
            pass

    decls = getattr(Table.hook.__func__, "__autoapi_hook_decls__")
    assert isinstance(decls[0], _HookDecl)
    assert decls[0].ops == ("create", "delete")


def test_hook_ctx_records_phase():
    class Table:
        @hook_ctx(ops="*", phase="POST_COMMIT")
        def hook(cls, ctx):
            pass

    decls = getattr(Table.hook.__func__, "__autoapi_hook_decls__")
    assert isinstance(decls[0], _HookDecl)
    assert decls[0].phase == "POST_COMMIT"
