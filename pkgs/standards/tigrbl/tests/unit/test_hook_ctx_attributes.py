from tigrbl.hook import HOOK_DECLS_ATTR, Hook, hook_ctx


def test_hook_ctx_marks_ctx_only():
    class Table:
        @hook_ctx(ops="create", phase="PRE_HANDLER")
        def before_create(cls, ctx):
            pass

    assert getattr(Table.before_create.__func__, "__tigrbl_ctx_only__") is True


def test_hook_ctx_records_ops():
    class Table:
        @hook_ctx(ops=("create", "delete"), phase="PRE_HANDLER")
        def hook(cls, ctx):
            pass

    decls = getattr(Table.hook.__func__, HOOK_DECLS_ATTR)
    assert isinstance(decls[0], Hook)
    assert decls[0].ops == ("create", "delete")


def test_hook_ctx_records_phase():
    class Table:
        @hook_ctx(ops="*", phase="POST_COMMIT")
        def hook(cls, ctx):
            pass

    decls = getattr(Table.hook.__func__, HOOK_DECLS_ATTR)
    assert isinstance(decls[0], Hook)
    assert decls[0].phase == "POST_COMMIT"
    assert decls[0].fn is Table.hook.__func__
