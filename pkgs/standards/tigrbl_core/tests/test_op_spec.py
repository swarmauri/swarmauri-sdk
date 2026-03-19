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

    decorated = [op for op in ops if op.alias == "demotable_get"]
    assert len(decorated) == 1
    assert decorated[0].alias == "demotable_get"
    assert decorated[0].target == "read"
    # Canonical ops are also generated for the table
    assert len(ops) >= 1
