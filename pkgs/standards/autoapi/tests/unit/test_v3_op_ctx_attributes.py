from autoapi.v3 import op_ctx
from autoapi.v3.decorators import collect_decorated_ops


def test_op_ctx_alias_sets_alias():
    class Model:
        @op_ctx(alias="custom_alias")
        def do(cls, ctx):
            return None

    spec = collect_decorated_ops(Model)[0]
    assert spec.alias == "custom_alias"


def test_op_ctx_target_sets_target():
    class Model:
        @op_ctx(target="create")
        def do(cls, ctx):
            return None

    spec = collect_decorated_ops(Model)[0]
    assert spec.target == "create"


def test_op_ctx_arity_sets_arity():
    class Model:
        @op_ctx(arity="collection")
        def do(cls, ctx):
            return None

    spec = collect_decorated_ops(Model)[0]
    assert spec.arity == "collection"


def test_op_ctx_rest_controls_exposure():
    class Model:
        @op_ctx(rest=False)
        def do(cls, ctx):
            return None

    spec = collect_decorated_ops(Model)[0]
    assert spec.expose_routes is False


def test_op_ctx_request_schema_attached():
    class Model:
        @op_ctx(request_schema="InputSchema")
        def do(cls, ctx):
            return None

    spec = collect_decorated_ops(Model)[0]
    assert spec.request_model == "InputSchema"


def test_op_ctx_response_schema_attached():
    class Model:
        @op_ctx(response_schema="OutputSchema")
        def do(cls, ctx):
            return None

    spec = collect_decorated_ops(Model)[0]
    assert spec.response_model == "OutputSchema"


def test_op_ctx_persist_policy_override():
    class Model:
        @op_ctx(persist="skip")
        def do(cls, ctx):
            return None

    spec = collect_decorated_ops(Model)[0]
    assert spec.persist == "skip"
