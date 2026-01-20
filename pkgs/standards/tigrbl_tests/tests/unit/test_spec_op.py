from tigrbl.op.decorators import alias_ctx, op_alias, op_ctx
from tigrbl.op.mro_collect import mro_collect_decorated_ops
from tigrbl.op.types import OpSpec


def test_op_spec_decorators_and_collection():
    class Widget:
        @op_ctx(alias="ping", target="custom", arity="member", persist="skip")
        def ping(cls, ctx):
            return None

    specs = mro_collect_decorated_ops(Widget)
    assert len(specs) == 1
    spec = specs[0]
    assert isinstance(spec, OpSpec)
    assert spec.alias == "ping"
    assert spec.target == "custom"
    assert spec.arity == "member"
    assert spec.persist == "skip"


def test_op_alias_and_alias_ctx_bindings():
    @op_alias(alias="fetch", target="read")
    @alias_ctx(read="fetch")
    class Gadget:
        pass

    ops = getattr(Gadget, "__tigrbl_ops__")
    assert any(op.alias == "fetch" for op in ops)
    alias_map = getattr(Gadget, "__tigrbl_aliases__")
    assert alias_map["read"] == "fetch"
