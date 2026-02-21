from __future__ import annotations

from types import SimpleNamespace

import pytest

from tigrbl.op import OpSpec
from tigrbl.runtime import events as _ev
from tigrbl.runtime import system as _sys
from tigrbl.runtime.kernel import Kernel


class _FakeDB:
    in_transaction = False

    def begin(self):
        self.in_transaction = True

    def commit(self):
        self.in_transaction = False

    def rollback(self):
        self.in_transaction = False


def _kernel() -> Kernel:
    return Kernel()


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("alias", "target"),
    [("read", "read"), ("create", "create")],
)
async def test_secdeps_execute_before_txn_begin_and_handler(
    alias: str, target: str
) -> None:
    events: list[str] = []

    def secdep_1(ctx):
        events.append("secdep_1")
        ctx.temp["secdep_1"] = True

    async def secdep_2(ctx):
        events.append("secdep_2")
        ctx.temp["secdep_2"] = True

    def dep_1(ctx):
        events.append("dep_1")
        ctx.temp["dep_1"] = True

    def handler(ctx):
        events.append("handler")
        ctx["result"] = {"ok": True}

    def begin(ctx):
        events.append("txn_begin")
        assert ctx.temp.get("secdep_1") is True
        assert ctx.temp.get("secdep_2") is True
        assert ctx.temp.get("dep_1") is True

    old_begin = _sys.INSTALLED.begin
    old_commit = _sys.INSTALLED.commit
    _sys.INSTALLED.begin = begin
    _sys.INSTALLED.commit = lambda _ctx: None
    try:

        class Model:
            pass

        Model.ops = SimpleNamespace(
            by_alias={
                alias: (
                    OpSpec(
                        alias=alias,
                        target=target,
                        table=Model,
                        handler=handler,
                        secdeps=(secdep_1, secdep_2),
                        deps=(dep_1,),
                    ),
                )
            }
        )
        Model.hooks = SimpleNamespace()
        setattr(Model.hooks, alias, SimpleNamespace(HANDLER=[handler]))

        k = _kernel()
        labels = k.plan_labels(Model, alias)
        assert labels.count(f"atom:dep:security@{_ev.PRE_TX_SECDEP}#0") == 1
        assert labels.count(f"atom:dep:security@{_ev.PRE_TX_SECDEP}#1") == 1
        assert labels.count(f"atom:dep:extras@{_ev.PRE_TX_DEP}#0") == 1

        result = await k.invoke(
            model=Model, alias=alias, db=_FakeDB(), request=None, ctx={}
        )
    finally:
        _sys.INSTALLED.begin = old_begin
        _sys.INSTALLED.commit = old_commit

    assert result == {"ok": True}
    assert events[:3] == ["secdep_1", "secdep_2", "dep_1"]
    if target == "create":
        assert events[3] == "txn_begin"
        assert events[-1] == "handler"
    else:
        assert "txn_begin" not in events


@pytest.mark.asyncio
async def test_secdep_failure_aborts_before_handler() -> None:
    ran_handler = False

    def secdep_fail(_ctx):
        raise RuntimeError("blocked")

    def handler(_ctx):
        nonlocal ran_handler
        ran_handler = True

    class Model:
        pass

    Model.ops = SimpleNamespace(
        by_alias={
            "create": (
                OpSpec(
                    alias="create",
                    target="create",
                    table=Model,
                    handler=handler,
                    secdeps=(secdep_fail,),
                ),
            )
        }
    )
    Model.hooks = SimpleNamespace(create=SimpleNamespace(HANDLER=[handler]))

    with pytest.raises(Exception):
        await _kernel().invoke(
            model=Model, alias="create", db=_FakeDB(), request=None, ctx={}
        )

    assert ran_handler is False
