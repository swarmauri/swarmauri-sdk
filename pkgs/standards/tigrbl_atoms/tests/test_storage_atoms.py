from __future__ import annotations

import asyncio
from types import SimpleNamespace

import pytest

from tigrbl_atoms.atoms.storage import REGISTRY
from tigrbl_atoms.atoms.storage import to_stored
from tigrbl_atoms.types import Atom, ResolvedCtx


def test_storage_registry_contains_expected_atoms() -> None:
    assert set(REGISTRY) == {("storage", "to_stored")}


def test_storage_registry_binds_expected_anchor_and_instance() -> None:
    assert REGISTRY[("storage", "to_stored")] == (to_stored.ANCHOR, to_stored.INSTANCE)


def test_storage_instance_and_impl_use_atom_contract() -> None:
    assert isinstance(to_stored.INSTANCE, Atom)
    assert issubclass(to_stored.AtomImpl, Atom)
    assert to_stored.INSTANCE.anchor == to_stored.ANCHOR


def test_to_stored_skips_when_persist_disabled() -> None:
    ctx = SimpleNamespace(persist=False, temp={})

    to_stored._run(None, ctx)

    assert ctx.temp == {}


def test_to_stored_transforms_assembled_field_and_assigns_model() -> None:
    model = SimpleNamespace(name=None)
    ctx = SimpleNamespace(
        temp={"assembled_values": {"name": "widget"}},
        opview=SimpleNamespace(
            schema_in=SimpleNamespace(
                fields=("name",),
                by_field={"name": {"nullable": False}},
            ),
            paired_index={},
            to_stored_transforms={"name": lambda value, _ctx: value.upper()},
        ),
        model=model,
    )

    to_stored._run(None, ctx)

    assert ctx.temp["assembled_values"]["name"] == "WIDGET"
    assert model.name == "WIDGET"
    assert {"field": "name", "action": "transformed"} in ctx.temp["storage_log"]


def test_to_stored_derives_paired_value_from_pointer_and_assigns_model() -> None:
    model = SimpleNamespace(token=None)
    ctx = SimpleNamespace(
        temp={
            "assembled_values": {},
            "paired_values": {"token": {"raw": "cleartext"}},
            "persist_from_paired": {
                "token": {"source": ("paired_values", "token", "raw")}
            },
        },
        opview=SimpleNamespace(
            schema_in=SimpleNamespace(
                fields=(),
                by_field={"token": {"nullable": False}},
            ),
            paired_index={"token": {"store": lambda raw, _ctx: f"hashed:{raw}"}},
            to_stored_transforms={},
        ),
        model=model,
    )

    to_stored._run(None, ctx)

    assert ctx.temp["assembled_values"]["token"] == "hashed:cleartext"
    assert model.token == "hashed:cleartext"
    assert {"field": "token", "action": "derived_from_paired"} in ctx.temp[
        "storage_log"
    ]


def test_to_stored_uses_paired_fallback_when_persist_pointer_missing() -> None:
    ctx = SimpleNamespace(
        temp={"assembled_values": {}, "paired_values": {"token": {"raw": "fallback"}}},
        opview=SimpleNamespace(
            schema_in=SimpleNamespace(
                fields=(),
                by_field={"token": {"nullable": True}},
            ),
            paired_index={"token": {"store": None}},
            to_stored_transforms={},
        ),
    )

    to_stored._run(None, ctx)

    assert ctx.temp["assembled_values"]["token"] == "fallback"


def test_to_stored_raises_when_non_nullable_paired_value_missing_before_flush() -> None:
    ctx = SimpleNamespace(
        temp={"assembled_values": {}},
        opview=SimpleNamespace(
            schema_in=SimpleNamespace(
                fields=(),
                by_field={"token": {"nullable": False}},
            ),
            paired_index={"token": {"store": lambda raw, _ctx: raw}},
            to_stored_transforms={},
        ),
    )

    with pytest.raises(RuntimeError, match="paired_missing_before_flush:token"):
        to_stored._run(None, ctx)

    assert {"field": "token", "error": "paired_missing_before_flush"} in ctx.temp[
        "storage_errors"
    ]


def test_storage_instance_promotes_resolved_ctx() -> None:
    ctx = ResolvedCtx(
        opview=SimpleNamespace(
            schema_in=SimpleNamespace(fields=(), by_field={}),
            paired_index={},
            to_stored_transforms={},
        )
    )

    out = asyncio.run(to_stored.INSTANCE(None, ctx))

    assert isinstance(out, ResolvedCtx)
