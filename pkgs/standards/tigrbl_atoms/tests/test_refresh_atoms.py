from __future__ import annotations

import asyncio
from types import SimpleNamespace

from tigrbl_atoms.atoms.refresh import REGISTRY
from tigrbl_atoms.atoms.refresh import demand
from tigrbl_atoms.types import Atom, OperatedCtx


def test_refresh_registry_contains_expected_atoms() -> None:
    assert set(REGISTRY) == {("refresh", "demand")}


def test_refresh_registry_binds_expected_anchor_and_instance() -> None:
    assert REGISTRY[("refresh", "demand")] == (demand.ANCHOR, demand.INSTANCE)


def test_refresh_instance_and_impl_use_atom_contract() -> None:
    assert isinstance(demand.INSTANCE, Atom)
    assert issubclass(demand.AtomImpl, Atom)
    assert demand.INSTANCE.anchor == demand.ANCHOR


def test_refresh_demand_auto_without_returning_defaults_to_true() -> None:
    ctx = SimpleNamespace(temp={}, opview=SimpleNamespace(refresh_hints=()))

    demand._run(None, ctx)

    assert ctx.temp["refresh_demand"] is True
    assert ctx.temp["refresh_fields"] == ()
    assert "policy=auto" in ctx.temp["refresh_reason"]


def test_refresh_demand_auto_with_returning_and_no_hints_skips_refresh() -> None:
    ctx = SimpleNamespace(
        temp={"used_returning": True},
        opview=SimpleNamespace(refresh_hints=()),
    )

    demand._run(None, ctx)

    assert ctx.temp["refresh_demand"] is False
    assert ctx.temp["refresh_reason"] == "skipped: returning_satisfied or policy=false"


def test_refresh_demand_always_policy_forces_refresh() -> None:
    ctx = SimpleNamespace(
        temp={"used_returning": True},
        cfg=SimpleNamespace(refresh_after_write=True),
        opview=SimpleNamespace(refresh_hints=()),
    )

    demand._run(None, ctx)

    assert ctx.temp["refresh_demand"] is True
    assert "policy=always" in ctx.temp["refresh_reason"]


def test_refresh_demand_never_policy_disables_refresh() -> None:
    ctx = SimpleNamespace(
        temp={},
        cfg=SimpleNamespace(refresh_after_write=False),
        opview=SimpleNamespace(refresh_hints=("updated_at",)),
    )

    demand._run(None, ctx)

    assert ctx.temp["refresh_demand"] is False
    assert ctx.temp["refresh_fields"] == ("updated_at",)


def test_refresh_demand_instance_promotes_operated_ctx() -> None:
    ctx = OperatedCtx()
    ctx.opview = SimpleNamespace(refresh_hints=("id",))

    out = asyncio.run(demand.INSTANCE(None, ctx))

    assert isinstance(out, OperatedCtx)
    assert out.temp["refresh_demand"] is True
    assert out.temp["refresh_fields"] == ("id",)
