from __future__ import annotations

import asyncio
from types import SimpleNamespace

from tigrbl_atoms.atoms.resolve import REGISTRY
from tigrbl_atoms.atoms.resolve import assemble, paired_gen
from tigrbl_atoms.types import Atom, ExecutingCtx, ResolvedCtx


def test_resolve_registry_contains_expected_atoms() -> None:
    assert set(REGISTRY) == {("resolve", "assemble"), ("resolve", "paired_gen")}


def test_resolve_registry_binds_expected_anchor_and_instance() -> None:
    assert REGISTRY[("resolve", "assemble")] == (assemble.ANCHOR, assemble.INSTANCE)
    assert REGISTRY[("resolve", "paired_gen")] == (
        paired_gen.ANCHOR,
        paired_gen.INSTANCE,
    )


def test_resolve_instances_and_impls_use_atom_contract() -> None:
    modules = (assemble, paired_gen)
    for module in modules:
        assert isinstance(module.INSTANCE, Atom)
        assert issubclass(module.AtomImpl, Atom)
        assert module.INSTANCE.anchor == module.ANCHOR


def test_assemble_builds_values_applies_default_and_tracks_virtuals() -> None:
    ctx = SimpleNamespace(
        payload={"name": "widget"},
        temp={},
        opview=SimpleNamespace(
            schema_in=SimpleNamespace(
                fields=("name", "status", "token"),
                by_field={
                    "name": {"in_enabled": True},
                    "status": {
                        "in_enabled": True,
                        "default_factory": lambda _ctx: "draft",
                    },
                    "token": {"in_enabled": True, "virtual": True},
                },
            )
        ),
    )

    assemble._run(None, ctx)

    assert ctx.temp["assembled_values"] == {"name": "widget", "status": "draft"}
    assert ctx.temp["virtual_in"] == {}
    assert set(ctx.temp["absent_fields"]) == {"status", "token"}
    assert ctx.temp["used_default_factory"] == ("status",)


def test_paired_gen_uses_virtual_input_then_sets_persist_pointer() -> None:
    ctx = SimpleNamespace(
        temp={"virtual_in": {"token_alias": "client-secret"}},
        opview=SimpleNamespace(
            paired_index={
                "token": {
                    "alias": "token_alias",
                    "gen": lambda _ctx: "generated-secret",
                    "mask_last": 2,
                }
            }
        ),
    )

    paired_gen._run(None, ctx)

    assert ctx.temp["paired_values"]["token"]["raw"] == "client-secret"
    assert ctx.temp["paired_values"]["token"]["alias"] == "token_alias"
    assert ctx.temp["persist_from_paired"]["token"]["source"] == (
        "paired_values",
        "token",
        "raw",
    )
    assert ctx.temp["response_extras"]["token_alias"] == "client-secret"


def test_paired_gen_generates_when_virtual_value_missing() -> None:
    ctx = SimpleNamespace(
        temp={},
        opview=SimpleNamespace(
            paired_index={"token": {"alias": "token_alias", "gen": lambda _ctx: "gen"}}
        ),
    )

    paired_gen._run(None, ctx)

    assert ctx.temp["paired_values"]["token"]["raw"] == "gen"
    assert ctx.temp["generated_paired"] == ("token",)


def test_resolve_instances_promote_executing_to_resolved_ctx() -> None:
    opview = SimpleNamespace(
        schema_in=SimpleNamespace(fields=(), by_field={}),
        paired_index={},
    )
    ctx = ExecutingCtx(opview=opview)

    assembled = asyncio.run(assemble.INSTANCE(None, ctx))
    generated = asyncio.run(paired_gen.INSTANCE(None, ctx))

    assert isinstance(assembled, ResolvedCtx)
    assert isinstance(generated, ResolvedCtx)
