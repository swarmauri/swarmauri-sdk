from __future__ import annotations

import sys
import types

from tigrbl_core._spec.op_spec import OpSpec


def test_apply_alias_returns_override_or_original() -> None:
    assert OpSpec.apply_alias("read", {"read": "fetch"}) == "fetch"
    assert OpSpec.apply_alias("delete", {"read": "fetch"}) == "delete"


def test_collect_uses_mro_collect_helper() -> None:
    module = types.ModuleType("tigrbl_canon.mapping.op_mro_collect")
    module.mro_collect_decorated_ops = lambda table: [
        OpSpec(alias="list", target="list"),
        OpSpec(alias=f"{table.__name__.lower()}_get", target="read"),
    ]
    sys.modules[module.__name__] = module

    class DemoTable:
        pass

    ops = OpSpec.collect(DemoTable)

    assert len(ops) == 2
    assert ops[0].alias == "list"
    assert ops[1].alias == "demotable_get"
