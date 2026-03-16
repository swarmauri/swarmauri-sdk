from __future__ import annotations

from tigrbl_core._spec.op_spec import OpSpec


def test_apply_alias_returns_override_or_original() -> None:
    assert OpSpec.apply_alias("read", {"read": "fetch"}) == "fetch"
    assert OpSpec.apply_alias("delete", {"read": "fetch"}) == "delete"


def test_collect_returns_decorated_op_specs() -> None:
    class DecoratedSpec:
        alias = "demotable_get"
        target = "read"
        arity = "member"
        persist = "default"

    def handler(ctx=None):
        return ctx

    handler.__tigrbl_op_spec__ = DecoratedSpec()

    class DemoTable:
        get = handler

    ops = OpSpec.collect(DemoTable)

    assert len(ops) == 1
    assert ops[0].alias == "demotable_get"
    assert ops[0].target == "read"
