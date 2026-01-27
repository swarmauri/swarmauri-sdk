from types import SimpleNamespace

from tigrbl import Api, App, op_ctx


def test_op_ctx_internal_binding_returns_classmethod_with_decl():
    @op_ctx(alias="search", target="custom", status_code=201)
    def search(cls, ctx):
        return ctx

    class Widget:
        lookup = search

    method = Widget.__dict__["lookup"]
    assert isinstance(method, classmethod)
    decl = method.__func__.__tigrbl_op_decl__
    assert decl.alias == "search"
    assert decl.target == "custom"
    assert decl.status_code == 201
    assert method.__func__.__tigrbl_ctx_only__ is True


def test_op_ctx_external_binding_to_multiple_table_classes():
    class Alpha:
        pass

    class Beta:
        pass

    @op_ctx(alias="touch", target="custom", bind=[Alpha, Beta])
    def touch(cls, ctx):
        return {"touched": True}

    for model in (Alpha, Beta):
        method = model.__dict__["touch"]
        assert isinstance(method, classmethod)
        decl = method.__func__.__tigrbl_op_decl__
        assert decl.alias == "touch"
        assert decl.target == "custom"


def test_op_ctx_binding_to_app_instance_uses_classmethod_descriptor():
    class ExampleApp(App):
        TITLE = "Example"
        VERSION = "0.1.0"
        LIFESPAN = None

    app = ExampleApp()

    @op_ctx(alias="diagnostics", target="custom", bind=app)
    def diagnostics(cls, ctx):
        return {"ok": True}

    bound = app.__dict__["diagnostics"]
    assert isinstance(bound, classmethod)
    assert bound.__func__.__tigrbl_op_decl__.alias == "diagnostics"


def test_op_ctx_binding_to_api_class():
    class ExampleApi(Api):
        PREFIX = ""
        NAME = "example"

    @op_ctx(alias="hook", target="custom", bind=ExampleApi)
    def hook(cls, ctx):
        return None

    method = ExampleApi.__dict__["hook"]
    assert isinstance(method, classmethod)
    assert method.__func__.__tigrbl_op_decl__.alias == "hook"


def test_op_ctx_binding_to_plain_object():
    target = SimpleNamespace()

    @op_ctx(alias="noop", target="custom", bind=target)
    def noop(cls, ctx):
        return None

    bound = target.__dict__["noop"]
    assert isinstance(bound, classmethod)
    assert bound.__func__.__tigrbl_op_decl__.alias == "noop"
