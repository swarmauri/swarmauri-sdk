from __future__ import annotations

import asyncio
from types import SimpleNamespace

from tigrbl_atoms.atoms.emit import REGISTRY
from tigrbl_atoms.atoms.emit import paired_post, paired_pre, readtime_alias
from tigrbl_atoms.types import Atom, EncodedCtx, ResolvedCtx


def test_emit_registry_contains_expected_atoms() -> None:
    assert set(REGISTRY) == {
        ("emit", "paired_pre"),
        ("emit", "paired_post"),
        ("emit", "readtime_alias"),
    }


def test_emit_registry_binds_expected_anchor_and_instance() -> None:
    assert REGISTRY[("emit", "paired_pre")] == (paired_pre.ANCHOR, paired_pre.INSTANCE)
    assert REGISTRY[("emit", "paired_post")] == (
        paired_post.ANCHOR,
        paired_post.INSTANCE,
    )
    assert REGISTRY[("emit", "readtime_alias")] == (
        readtime_alias.ANCHOR,
        readtime_alias.INSTANCE,
    )


def test_emit_instances_and_impls_use_atom_contract() -> None:
    modules = (paired_pre, paired_post, readtime_alias)
    for module in modules:
        assert isinstance(module.INSTANCE, Atom)
        assert issubclass(module.AtomImpl, Atom)
        assert module.INSTANCE.anchor == module.ANCHOR


def test_paired_pre_queues_deferred_alias_from_paired_values() -> None:
    ctx = SimpleNamespace(
        persist=True,
        temp={"paired_values": {"token": {"raw": "secret", "alias": "token_alias"}}},
        opview=SimpleNamespace(paired_index={}),
    )

    paired_pre._run(None, ctx)

    queued = ctx.temp["emit_aliases"]["pre"]
    assert len(queued) == 1
    assert queued[0]["field"] == "token"
    assert queued[0]["alias"] == "token_alias"
    assert queued[0]["source"] == ("paired_values", "token", "raw")


def test_paired_post_emits_to_response_extras_and_scrubs_raw() -> None:
    ctx = SimpleNamespace(
        persist=True,
        temp={
            "emit_aliases": {
                "pre": [
                    {
                        "field": "token",
                        "alias": "token_alias",
                        "source": ("paired_values", "token", "raw"),
                        "meta": {"k": "v"},
                    }
                ],
                "post": [],
                "read": [],
            },
            "paired_values": {"token": {"raw": "secret"}},
        },
    )

    paired_post._run(None, ctx)

    assert ctx.temp["response_extras"]["token_alias"] == "secret"
    assert ctx.temp["emit_aliases"]["pre"] == []
    assert ctx.temp["emit_aliases"]["post"][0]["alias"] == "token_alias"
    assert ctx.temp["paired_values"]["token"]["emitted"] is True
    assert "raw" not in ctx.temp["paired_values"]["token"]


def test_readtime_alias_emits_masked_sensitive_alias() -> None:
    ctx = SimpleNamespace(
        temp={
            "emit_aliases": {"pre": [], "post": [], "read": []},
            "response_extras": {},
        },
        opview=SimpleNamespace(
            schema_out=SimpleNamespace(
                fields=("token",),
                by_field={
                    "token": {
                        "alias_out": "token_masked",
                        "sensitive": True,
                        "mask_last": 2,
                    }
                },
                expose=("token",),
            )
        ),
    )
    obj = SimpleNamespace(token="abcd1234")

    readtime_alias._run(obj, ctx)

    assert ctx.temp["response_extras"]["token_masked"] == "••••••34"
    assert ctx.temp["emit_aliases"]["read"][0]["alias"] == "token_masked"


def test_emit_instance_promotions_keep_ctx_type() -> None:
    resolved = ResolvedCtx()
    encoded = EncodedCtx()
    encoded.opview = SimpleNamespace(
        schema_out=SimpleNamespace(fields=(), by_field={}, expose=())
    )
    resolved_out = asyncio.run(paired_pre.INSTANCE(None, resolved))
    encoded_out = asyncio.run(paired_post.INSTANCE(None, encoded))
    read_out = asyncio.run(readtime_alias.INSTANCE(None, encoded))

    assert isinstance(resolved_out, ResolvedCtx)
    assert isinstance(encoded_out, EncodedCtx)
    assert isinstance(read_out, EncodedCtx)
