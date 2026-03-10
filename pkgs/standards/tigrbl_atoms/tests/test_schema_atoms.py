from __future__ import annotations

import asyncio
from types import SimpleNamespace

import pytest

from tigrbl_atoms.atoms.schema import REGISTRY
from tigrbl_atoms.atoms.schema import collect_in, collect_out
from tigrbl_atoms.types import Atom, ExecutingCtx, OperatedCtx


def test_schema_registry_contains_expected_atoms() -> None:
    assert set(REGISTRY) == {("schema", "collect_in"), ("schema", "collect_out")}


def test_schema_registry_binds_expected_anchor_and_instance() -> None:
    assert REGISTRY[("schema", "collect_in")] == (
        collect_in.ANCHOR,
        collect_in.INSTANCE,
    )
    assert REGISTRY[("schema", "collect_out")] == (
        collect_out.ANCHOR,
        collect_out.INSTANCE,
    )


def test_schema_instances_and_impls_use_atom_contract() -> None:
    modules = (collect_in, collect_out)
    for module in modules:
        assert isinstance(module.INSTANCE, Atom)
        assert issubclass(module.AtomImpl, Atom)
        assert module.INSTANCE.anchor == module.ANCHOR


def test_collect_in_populates_schema_in_when_missing() -> None:
    ctx = SimpleNamespace(
        temp={},
        opview=SimpleNamespace(
            schema_in=SimpleNamespace(
                fields=("name", "age"),
                by_field={
                    "name": {"required": True},
                    "age": {"required": False},
                },
            )
        ),
    )

    collect_in._run(None, ctx)

    assert ctx.temp["schema_in"]["fields"] == ("name", "age")
    assert ctx.temp["schema_in"]["required"] == ("name",)


def test_collect_out_populates_schema_out_when_missing() -> None:
    ctx = SimpleNamespace(
        temp={},
        opview=SimpleNamespace(
            schema_out=SimpleNamespace(
                fields=("name",),
                by_field={"name": {"alias_out": "name"}},
                expose=("name",),
            )
        ),
    )

    collect_out._run(None, ctx)

    assert ctx.temp["schema_out"]["fields"] == ("name",)
    assert ctx.temp["schema_out"]["expose"] == ("name",)


def test_collect_atoms_raise_when_opview_missing() -> None:
    with pytest.raises(RuntimeError, match="ctx_missing:opview"):
        collect_in._run(None, SimpleNamespace(temp={}))
    with pytest.raises(RuntimeError, match="ctx_missing:opview"):
        collect_out._run(None, SimpleNamespace(temp={}))


def test_schema_instances_promote_ctx_types() -> None:
    ov = SimpleNamespace(
        schema_in=SimpleNamespace(fields=(), by_field={}),
        schema_out=SimpleNamespace(fields=(), by_field={}, expose=()),
    )
    executing = ExecutingCtx(opview=ov)
    operated = OperatedCtx(opview=ov)

    executing_out = asyncio.run(collect_in.INSTANCE(None, executing))
    operated_out = asyncio.run(collect_out.INSTANCE(None, operated))

    assert isinstance(executing_out, ExecutingCtx)
    assert isinstance(operated_out, OperatedCtx)
